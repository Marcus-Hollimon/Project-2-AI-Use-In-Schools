"""Turn Claude Code transcript records into deduplicated token and contribution data.

Pure functions over already-parsed records, so tests can feed small made-up transcripts.
The rules come from measurements, not assumptions (evidence/session1-audit, evidence/phase1-recon):
- One API response is saved as several rows that repeat the same usage: count each message.id once.
- Resuming a session copies earlier records into a new file: skip records whose uuid was already
  seen, and count each message.id once across all files.
- A /compact is a `system` record with subtype `compact_boundary`. The model call that writes the
  summary leaves no record, so its cost is reported as a known gap.
- Marcus's prompts are `user` records with origin.kind == "human" that are neither meta records
  nor the compact summary. Everything else typed as `user` (tool results, slash-command echoes,
  hook output, reminders) is not a prompt.
"""
import re
from datetime import datetime

CLASSES = ("input", "cacheWrite", "cacheRead", "output")
COMMAND_NAME = re.compile(r"<command-name>(.*?)</command-name>", re.S)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
SHELL_TOOLS = ("Bash", "PowerShell")
TEST_STARTERS = ("uv", "python", "python3", "pytest", "npx", "npm", "vitest")
TEST_WORDS = re.compile(r"\b(pytest|vitest)\b|record_tests\.py|^npm\s+(run\s+)?test(:record)?(\s|$)")
RECORDERS = re.compile(r"record_tests\.py|test:record")


def classify_test_command(command):
    """"recorded", "unrecorded" or None for a shell command Claude ran.

    A command is split into its parts (at newlines, ;, &&, || and |). A part runs tests when its
    first word starts a program (uv, python, pytest, npx, npm, vitest) and it names a test runner or
    a recorder, so `grep pytest file` or a commit message that mentions pytest does not count."""
    found = None
    for part in re.split(r"\n|;|&&|\|\||\|", command or ""):
        part = part.strip()
        words = part.split()
        if not words or words[0] not in TEST_STARTERS or not TEST_WORDS.search(part):
            continue
        if RECORDERS.search(part):
            return "recorded"
        found = "unrecorded"
    return found


def parse_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def usage_classes(usage):
    details = usage.get("output_tokens_details") or {}
    return {
        "input": usage.get("input_tokens") or 0,
        "cacheWrite": usage.get("cache_creation_input_tokens") or 0,
        "cacheRead": usage.get("cache_read_input_tokens") or 0,
        "output": usage.get("output_tokens") or 0,
        "thinking": details.get("thinking_tokens") or 0,
    }


def context_size(classes):
    return classes["input"] + classes["cacheWrite"] + classes["cacheRead"]


def _message(record):
    """The record's message. An assistant record with model "<synthetic>" is a placeholder the app
    writes itself (seen 2026-11-11 at 19:40 EST: "No response requested." after a /compact, all usage
    zero, no api-request before it). It is not a model response, so it is returned as no message."""
    message = record.get("message")
    if not isinstance(message, dict) or message.get("model") == "<synthetic>":
        return {}
    return message


def _blocks(message):
    content = message.get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return []


def _text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def is_prompt(record):
    return (
        record.get("type") == "user"
        and (record.get("origin") or {}).get("kind") == "human"
        and not record.get("isMeta")
        and not record.get("isCompactSummary")
    )


def walk(files):
    """files: list of dicts {session, subagent (bool), rows (parsed records in file order)}.

    Returns everything later steps need: deduplicated responses, naive row sums, segments,
    compact boundaries, per-file counts for the completeness check, and turns.
    """
    seen_uuids = set()
    seen_responses = set()
    responses = []
    naive = {k: 0 for k in CLASSES}
    usage_rows = 0
    segments = []
    boundaries = []
    file_stats = []
    turns = []
    events = []  # Marcus's slash commands and answers to Claude's questions
    ask_ids = set()
    tool_ids = set()
    test_ids = set()
    test_commands = []  # every shell command of Claude's that ran tests, and whether it was recorded
    segment = None
    turn = None

    def new_segment(time, reason, session):
        seg = {"id": len(segments) + 1, "session": session, "start": time, "startReason": reason, "endReason": None}
        segments.append(seg)
        return seg

    for f in files:
        rows = f["rows"]
        session = f["session"]
        api_requests = sum(1 for r in rows if r.get("type") == "api-request")
        ids_in_file = []
        request_indexes = [i for i, r in enumerate(rows) if r.get("type") == "api-request"]
        assistant_indexes = [i for i, r in enumerate(rows) if r.get("type") == "assistant" and _message(r)]
        last_request_index = request_indexes[-1] if request_indexes else -1
        last_assistant_index = assistant_indexes[-1] if assistant_indexes else -1
        # A request followed by another request with no response in between was never answered
        # (seen once on 2026-11-08: two requests 0.6 s apart, no error record). Listed, not hidden.
        unanswered = [rows[a].get("timestamp") for a, b in zip(request_indexes, request_indexes[1:])
                      if not any(a < i < b for i in assistant_indexes)]
        last_response = None
        # Whether the last main-session response had a thinking block. The transcript keeps only its
        # signature, not its text, so a compact right after it can report more tokens than we can count.
        last_mid, last_thinking = None, False
        after_last_response = []  # user records (tool results, prompts) the model never answered
        first_new = True
        for index, record in enumerate(rows):
            message = _message(record)
            usage = message.get("usage")
            if record.get("type") == "assistant" and usage:
                usage_rows += 1
                classes = usage_classes(usage)
                for k in CLASSES:
                    naive[k] += classes[k]
                mid = message.get("id")
                if mid and mid not in ids_in_file:
                    ids_in_file.append(mid)
            uuid = record.get("uuid")
            if uuid:
                if uuid in seen_uuids:
                    continue  # copied by a resume: already counted from the original file
                seen_uuids.add(uuid)
                if first_new and not f.get("subagent"):
                    first_new = False
                    reason = "resume" if index > 0 and any(r.get("uuid") in seen_uuids for r in rows[:index]) else "new session or /clear"
                    if segment is not None and segment["endReason"] is None:
                        segment["endReason"] = reason
                    segment = new_segment(record.get("timestamp"), reason, session)
            if segment is None and f.get("subagent"):
                segment = new_segment(record.get("timestamp"), "new session or /clear", session)

            if record.get("type") == "system" and record.get("subtype") == "compact_boundary":
                meta = record.get("compactMetadata") or {}
                expected = context_size(last_response) + last_response["output"] if last_response else None
                boundaries.append({
                    "time": record.get("timestamp"),
                    "session": session,
                    "trigger": meta.get("trigger"),
                    "preTokens": meta.get("preTokens"),
                    "postTokens": meta.get("postTokens"),
                    "durationMs": meta.get("durationMs"),
                    "lastResponseContextPlusOutput": expected,
                    "unansweredAfter": list(after_last_response),
                    "lastResponseHadThinking": last_thinking,
                })
                segment["endReason"] = "/compact"
                segment = new_segment(record.get("timestamp"), "/compact", session)
                continue

            if record.get("type") == "user" and not f.get("subagent") and message.get("content"):
                after_last_response.append(record.get("timestamp"))

            if record.get("type") == "assistant" and usage:
                mid = message.get("id")
                classes = usage_classes(usage)
                if mid and mid not in seen_responses:
                    seen_responses.add(mid)
                    entry = {"id": mid, "time": record.get("timestamp"), "session": session,
                             "model": message.get("model"), "segment": segment["id"],
                             "subagent": bool(f.get("subagent"))}
                    entry.update(classes)
                    responses.append(entry)
                if not f.get("subagent"):
                    last_response = classes
                    if mid != last_mid:
                        last_mid, last_thinking = mid, False
                    last_thinking = last_thinking or any(b.get("type") == "thinking" for b in _blocks(message))
                    after_last_response = []
                for block in _blocks(message):
                    if block.get("type") == "tool_use":
                        if block.get("name") in SHELL_TOOLS and block.get("id") not in test_ids:
                            test_ids.add(block.get("id"))
                            kind = classify_test_command((block.get("input") or {}).get("command"))
                            if kind:
                                test_commands.append({"time": record.get("timestamp"), "kind": kind})
                        if block.get("name") == "AskUserQuestion":
                            ask_ids.add(block.get("id"))
                        if turn is not None and block.get("id") not in tool_ids:
                            tool_ids.add(block.get("id"))
                            turn["toolCalls"] += 1
                    elif block.get("type") == "text" and turn is not None and not f.get("subagent"):
                        if turn["lastReplyId"] != mid:
                            turn["lastReplyId"] = mid
                            turn["reply"] = []
                            turn["replyTime"] = record.get("timestamp")
                        turn["reply"].append(block.get("text", ""))
                continue

            if f.get("subagent") or record.get("type") != "user":
                continue
            if is_prompt(record):
                blocks = _blocks(message)
                turn = {"promptId": record.get("promptId") or uuid, "time": record.get("timestamp"),
                        "session": session, "segment": segment["id"],
                        "text": "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text"),
                        "images": sum(1 for b in blocks if b.get("type") == "image"),
                        "reply": [], "replyTime": None, "lastReplyId": None, "toolCalls": 0}
                turns.append(turn)
                continue
            content = message.get("content")
            if isinstance(content, str) and "<command-name>" in content:
                name = COMMAND_NAME.search(content)
                args = COMMAND_ARGS.search(content)
                events.append({"time": record.get("timestamp"), "kind": "command",
                               "text": (name.group(1).strip() + " " + (args.group(1).strip() if args else "")).strip()})
                continue
            for block in _blocks(message):
                if block.get("type") == "tool_result" and block.get("tool_use_id") in ask_ids:
                    events.append({"time": record.get("timestamp"), "kind": "answer",
                                   "text": _text_of(block.get("content"))})

        in_flight_ok = last_request_index > last_assistant_index
        file_stats.append({"session": session, "subagent": bool(f.get("subagent")),
                           "apiRequests": api_requests, "uniqueResponses": len(ids_in_file),
                           "unansweredRequests": unanswered,
                           "newestRecordIsUnansweredRequest": in_flight_ok})

    for t in turns:
        t["reply"] = "\n\n".join(t["reply"]).strip()
        del t["lastReplyId"]
    return {"responses": responses, "naive": naive, "usageRows": usage_rows, "segments": segments,
            "boundaries": boundaries, "fileStats": file_stats, "turns": turns, "events": events,
            "testCommands": test_commands}


def totals(responses, key):
    """Sum the four classes (plus thinking) grouped by responses' `key` field."""
    out = {}
    for r in responses:
        group = out.setdefault(r[key], {"responses": 0, "input": 0, "cacheWrite": 0, "cacheRead": 0,
                                        "output": 0, "thinking": 0, "contextSum": 0})
        group["responses"] += 1
        for k in CLASSES + ("thinking",):
            group[k] += r[k]
        group["contextSum"] += context_size(r)
    for group in out.values():
        group["averageContext"] = round(group.pop("contextSum") / group["responses"]) if group["responses"] else 0
    return out


def check_context(readings, responses, window_s=120):
    """C1: each app context reading lies between the context sizes of two consecutive main-session
    responses, the first of them within `window_s` of the reading.

    The app is read while a response's tool calls run, so its number sits between that response's
    context and the next one's. (Amended 2026-11-11: the first rule, "within 0.5% of one response",
    failed when the response taking the reading wrote a large file. Evidence in the Phase 1 spec.)
    The nearest single response is still reported, so the size of the gap stays visible.
    """
    main = [r for r in responses if not r.get("subagent")]
    results = []
    for reading in readings:
        if not reading.get("context"):
            continue
        when = parse_time(reading["time"])
        value = reading["context"]
        bracket = None
        for a, b in zip(main, main[1:]):
            if abs((parse_time(a["time"]) - when).total_seconds()) <= window_s and context_size(a) <= value <= context_size(b):
                bracket = (a["time"], context_size(a), context_size(b))
                break
        near = [r for r in main if abs((parse_time(r["time"]) - when).total_seconds()) <= window_s]
        best = min(near, key=lambda r: abs(context_size(r) - value)) if near else None
        results.append({"reading": reading["time"], "app": value,
                        "between": [bracket[1], bracket[2]] if bracket else None,
                        "responseTime": bracket[0] if bracket else None,
                        "nearestDifference": abs(context_size(best) - value) if best else None,
                        "pass": bracket is not None})
    return results


def check_completeness(file_stats, live_session):
    """C2: every api-request record has a response, except ones listed as unanswered (a request
    followed by another request with no response between) and, only for the live session's newest
    record, the request in flight."""
    results = []
    for s in file_stats:
        extra = s["apiRequests"] - s["uniqueResponses"] - len(s.get("unansweredRequests", []))
        ok = extra == 0 or (extra == 1 and s["session"] == live_session and s["newestRecordIsUnansweredRequest"])
        results.append(dict(s, extra=extra, pass_=ok))
    for r in results:
        r["pass"] = r.pop("pass_")
    return results


def check_compacts(boundaries):
    """C3: a boundary's tokens-before equals the last response's context plus its output, exactly.

    Two exceptions, each passing only when tokens-before is larger, with the difference listed:
    - the turn was stopped (seen 2026-11-11 12:45 EST): the tool result and the interrupt note sit
      after the last response and were never sent to the model; their times are listed.
    - the last response had a thinking block (Marcus, 2026-11-11 evening): the transcript keeps only
      the block's signature, so its size cannot be counted. All 3 of 20 real compacts that missed the
      exact rule (12:45, 15:59, 16:12 EST; 415 to 721 tokens over) followed such a response, and all
      17 that followed a response without one matched exactly."""
    results = []
    for b in boundaries:
        pre, computed = b["preTokens"], b["lastResponseContextPlusOutput"]
        unanswered = b.get("unansweredAfter") or []
        thinking = bool(b.get("lastResponseHadThinking"))
        exact = pre is not None and pre == computed
        larger = pre is not None and computed is not None and pre > computed
        stopped = larger and bool(unanswered)
        hidden = larger and thinking
        r = {"time": b["time"], "preTokens": pre, "computed": computed, "pass": exact or stopped or hidden}
        if (stopped or hidden) and not exact:
            r["difference"] = pre - computed
            if stopped:
                r["unansweredAfter"] = unanswered
            if hidden:
                r["lastResponseHadThinking"] = True
        results.append(r)
    return results


def assign_phases(responses, readings):
    """Phase of a response = phase of the latest usage reading at or before it; earlier = planning."""
    ordered = sorted(((parse_time(r["time"]), r["phase"]) for r in readings), key=lambda x: x[0])
    for resp in responses:
        when = parse_time(resp["time"])
        phase = "planning"
        for t, p in ordered:
            if t <= when:
                phase = p
        resp["phase"] = phase
    return responses
