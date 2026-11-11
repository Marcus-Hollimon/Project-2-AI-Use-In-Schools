"""Build the derived data for the Contributions and Token usage tabs.

Reads only the transcripts listed in pipeline/sessions.json (plus their subagent files), the
progress records, and git history. Writes data/derived/{tokens,contributions,checks}.json and a
private preview of every question and answer to private/qa-preview.md (gitignored).

Run from the repo root:  uv run --project pipeline python pipeline/build.py
"""
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as tx  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKSLASH = chr(92)


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # a line still being written by the live session
    return rows


def load_files(config):
    files = []
    base = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    for s in config["sessions"]:
        folder = os.path.join(base, s["projectDir"])
        main = os.path.join(folder, s["id"] + ".jsonl")
        files.append({"session": s["id"], "subagent": False, "rows": read_jsonl(main)})
        for sub in sorted(glob.glob(os.path.join(folder, s["id"], "subagents", "*.jsonl"))):
            files.append({"session": s["id"], "subagent": True, "rows": read_jsonl(sub)})
    return files


def table_rows(path):
    """Rows of every Markdown table in a file whose first cell is a date (2026-...)."""
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("| 20"):
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


def iso(text):
    """Normalize an ISO time with offset (minutes optional) for sorting and display."""
    return tx.parse_time(text).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


PHASES = {"planning", "0", "1", "2", "3", "4", "5", "6"}


def parse_readings(rows):
    """Usage readings from table rows. A malformed row stops the build instead of shifting columns:
    on 2026-11-11 seven rows written with 5 cells made "66" the moment and "195,190" the weekly %."""
    readings = []
    for cells in rows:
        problem = None
        if len(cells) != 7:
            problem = "has %d cells, expected 7" % len(cells)
        elif cells[1] not in PHASES:
            problem = "phase %r is not one of %s" % (cells[1], sorted(PHASES))
        elif not all(re.fullmatch(r"\d+|not read", c) for c in cells[3:5]):
            problem = "5-hour and weekly must be whole percentages or 'not read'"
        if problem:
            raise ValueError("progress/usage.md row %s: %s" % (cells[0], problem))
        digits = re.sub(r"[^0-9]", "", cells[5])
        readings.append({"time": iso(cells[0]), "phase": cells[1], "moment": cells[2],
                         "fiveHour": cells[3], "weekly": cells[4],
                         "context": int(digits) if digits else None, "reset": cells[6]})
    return readings


def read_readings():
    return parse_readings(table_rows(os.path.join(ROOT, "progress", "usage.md")))


def read_milestones():
    return [{"time": iso(c[0]), "actor": c[2], "kind": "milestone", "phase": c[1], "text": c[3], "evidence": c[4]}
            for c in table_rows(os.path.join(ROOT, "progress", "log.md"))]


def read_decisions():
    return [{"time": iso(c[0]), "actor": c[3], "kind": "decision", "text": c[1], "options": c[2], "notes": c[4]}
            for c in table_rows(os.path.join(ROOT, "progress", "decisions.md"))]


def read_commits():
    sep, end = chr(31), chr(30)
    fmt = "%h" + "%x1f" + "%aI" + "%x1f" + "%s" + "%x1f" + "%(trailers:key=Co-Authored-By,valueonly,separator=;)" + "%x1e"
    out = subprocess.run(["git", "log", "--format=" + fmt], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    commits = []
    for chunk in out.split(end):
        parts = chunk.strip().split(sep)
        if len(parts) < 4:
            continue
        by_claude = "Claude" in parts[3]
        commits.append({"time": iso(parts[1]), "actor": "Claude" if by_claude else "Marcus", "kind": "commit",
                        "text": parts[2], "commit": parts[0],
                        "note": "written by Claude, pushed from Marcus's account" if by_claude else ""})
    return commits


def read_runs():
    """Every recorded test run, oldest first (file names start with the run's UTC start time)."""
    runs = []
    for path in sorted(glob.glob(os.path.join(ROOT, "validation", "runs", "*.json"))):
        run = json.load(open(path, encoding="utf-8"))
        run["file"] = os.path.basename(path)
        runs.append(run)
    return runs


def check_claims(claims, runs):
    """C5: each test named in the claims register passed in the newest recorded run of its suite.

    A web test cannot see the result of the run it is part of, so this is checked here, after the
    runs are recorded. One result per (claim, test)."""
    newest = {}
    for run in runs:
        newest[run["suite"]] = run  # runs are oldest first, so the last one per suite wins
    results = []
    for claim in claims:
        for t in claim.get("tests", []):
            run = newest.get(t["suite"])
            found = [a for f in (run or {}).get("report", {}).get("testResults", [])
                     for a in f.get("assertionResults", []) if a.get("title") == t["test"]]
            status = found[0]["status"] if found else "not in the newest run"
            results.append({"claim": claim["id"], "suite": t["suite"], "test": t["test"],
                            "run": run["file"] if run else None, "status": status, "pass": status == "passed"})
    return results


def check_mutations(runs):
    """C6: every mutation run (label starting "mutation") failed, and a later run of the same suite
    that is not a mutation passed. Checked here, after recording, because a test cannot see the run
    it is part of (found 2026-11-11: a web test of this rule failed its own clean run)."""
    results = []
    for i, run in enumerate(runs):
        if not re.match(r"mutation", run.get("label") or "", re.I):
            continue
        later = [r for r in runs[i + 1:] if r["suite"] == run["suite"] and not re.match(r"mutation", r.get("label") or "", re.I)]
        passing = next((r for r in later if r["summary"]["failed"] == 0), None)
        results.append({"run": run["file"], "suite": run["suite"], "label": run["label"],
                        "failed": run["summary"]["failed"], "laterPassingRun": passing["file"] if passing else None,
                        "pass": run["summary"]["failed"] > 0 and passing is not None})
    return results


def git_email():
    r = subprocess.run(["git", "config", "user.email"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip()


def make_scrubber():
    home = os.path.expanduser("~")
    parts = [p for p in home.replace(BACKSLASH, "/").split("/") if p]
    variants = {BACKSLASH.join(parts), (BACKSLASH * 2).join(parts), "/".join(parts)}
    if parts and parts[0].endswith(":"):
        variants.add("/" + parts[0][0].lower() + "/" + "/".join(parts[1:]))
    patterns = [re.compile(re.escape(v), re.I) for v in sorted(variants, key=len, reverse=True)]
    email = git_email()
    email_re = re.compile(re.escape(email), re.I) if email else None

    def scrub(text):
        if not isinstance(text, str):
            return text
        for p in patterns:
            text = p.sub("~", text)
        if email_re:
            text = email_re.sub("[email removed]", text)
        return text

    leaks = patterns + ([email_re] if email_re else [])
    return scrub, leaks


def scrub_all(value, scrub):
    if isinstance(value, dict):
        return {k: scrub_all(v, scrub) for k, v in value.items()}
    if isinstance(value, list):
        return [scrub_all(v, scrub) for v in value]
    return scrub(value)


def main():
    config = json.load(open(os.path.join(ROOT, "pipeline", "sessions.json"), encoding="utf-8"))
    exclusions = json.load(open(os.path.join(ROOT, "progress", "prompt-exclusions.json"), encoding="utf-8"))
    hidden = set(exclusions.get("hide", []))
    files = load_files(config)
    walked = tx.walk(files)
    readings = read_readings()
    responses = tx.assign_phases(walked["responses"], readings)
    live = config["sessions"][-1]["id"]

    checks = {
        "C1_context": tx.check_context(readings, responses),
        "C2_completeness": tx.check_completeness(walked["fileStats"], live),
        "C3_compact": tx.check_compacts(walked["boundaries"]),
        "C5_claims": check_claims(json.load(open(os.path.join(ROOT, "validation", "claims.json"),
                                                 encoding="utf-8"))["claims"], read_runs()),
        "C6_mutations": check_mutations(read_runs()),
    }
    commands = walked["testCommands"]
    checks["testCommands"] = {
        "recorded": sum(1 for c in commands if c["kind"] == "recorded"),
        "unrecorded": sum(1 for c in commands if c["kind"] == "unrecorded"),
        "first": min((c["time"] for c in commands), default=None),
        "rule": "shell commands Claude ran whose program is uv, python, pytest, npx, npm or vitest and that "
                "name pytest, vitest, npm test or a recorder; recorded = through record_tests.py or test:record",
    }
    dedup = {k: sum(r[k] for r in responses) for k in tx.CLASSES}
    checks["C4_inflation"] = {"usageRows": walked["usageRows"], "uniqueResponses": len(responses),
                              "naive": walked["naive"], "deduplicated": dedup}

    tokens = {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classes": list(tx.CLASSES), "note": "thinking is part of output, never added on top",
        "responses": [{k: r[k] for k in ("time", "model", "phase", "segment", "subagent", "input", "cacheWrite",
                                         "cacheRead", "output", "thinking")} | {"session": r["session"][:8]}
                      for r in responses],
        "totals": dedup | {"thinking": sum(r["thinking"] for r in responses), "responses": len(responses)},
        "byPhase": tx.totals(responses, "phase"),
        "bySegment": tx.totals(responses, "segment"),
        "segments": [dict(s, session=s["session"][:8]) for s in walked["segments"]],
        "resets": [dict(b, session=b["session"][:8]) for b in walked["boundaries"]],
        "readings": readings,
        "gaps": [{"time": b["time"], "what": "the model call that wrote this /compact summary is not in the transcript",
                  "itRead": b["preTokens"]} for b in walked["boundaries"]]
        + [{"time": t, "what": "a request with no response recorded (another request followed it); any cost is unknown",
            "itRead": None} for s in walked["fileStats"] for t in s["unansweredRequests"]],
    }

    entries = []
    for i, t in enumerate(walked["turns"], start=1):
        if t["promptId"] in hidden:
            entries.append({"time": t["time"], "actor": "Marcus", "kind": "prompt", "turn": i, "text": "[hidden by Marcus]"})
            continue
        prompt_text = t["text"] + (("\n[%d image(s) attached, not published]" % t["images"]) if t["images"] else "")
        entries.append({"time": t["time"], "actor": "Marcus", "kind": "prompt", "turn": i, "text": prompt_text})
        entries.append({"time": t["replyTime"] or t["time"], "actor": "Claude", "kind": "reply", "turn": i,
                        "text": t["reply"], "toolCalls": t["toolCalls"]})
    for e in walked["events"]:
        entries.append({"time": e["time"], "actor": "Marcus", "kind": e["kind"], "text": e["text"]})
    entries += read_milestones() + read_decisions() + read_commits()
    for e in entries:
        e["time"] = iso(e["time"])
    # Milestones carry the phase written in log.md; every other entry gets the phase of the
    # latest usage reading at or before it, the same rule as token responses.
    tx.assign_phases([e for e in entries if "phase" not in e], readings)
    entries.sort(key=lambda e: e["time"])

    scrub, leaks = make_scrubber()
    contributions = scrub_all({"generatedAt": tokens["generatedAt"], "entries": entries}, scrub)
    tokens = scrub_all(tokens, scrub)

    out_dir = os.path.join(ROOT, "data", "derived")
    os.makedirs(out_dir, exist_ok=True)
    blobs = {"tokens.json": json.dumps(tokens, indent=1, ensure_ascii=False),
             "contributions.json": json.dumps(contributions, indent=1, ensure_ascii=False)}
    forbidden = [p.pattern for p in leaks] + ["tool_use_id", "tool_result", "api-request-blob"]
    checks["privacy"] = [{"file": name, "pattern": "(hidden)" if i < len(leaks) else pat,
                          "hits": len(re.findall(pat if i >= len(leaks) else leaks[i], blob)),
                          "pass": len(re.findall(pat if i >= len(leaks) else leaks[i], blob)) == 0}
                         for name, blob in blobs.items() for i, pat in enumerate(forbidden)]
    for name, blob in blobs.items():
        open(os.path.join(out_dir, name), "w", encoding="utf-8").write(blob + "\n")
    all_pass = all(c["pass"] for key in ("C1_context", "C2_completeness", "C3_compact", "C5_claims", "C6_mutations", "privacy") for c in checks[key])
    checks["allPass"] = all_pass
    open(os.path.join(out_dir, "checks.json"), "w", encoding="utf-8").write(json.dumps(checks, indent=1) + "\n")

    private = os.path.join(ROOT, "private")
    os.makedirs(private, exist_ok=True)
    lines = ["# Questions and answers preview (private, never uploaded)", "",
             "Every turn as it would be published. To hide one, tell Claude its turn number.", ""]
    for e in contributions["entries"]:
        if e["kind"] in ("prompt", "reply"):
            lines += ["## Turn %s, %s, %s" % (e.get("turn"), e["actor"], e["time"]), "", e["text"], ""]
    open(os.path.join(private, "qa-preview.md"), "w", encoding="utf-8").write("\n".join(lines))

    last = [r for r in responses if r["session"] == live and not r["subagent"]]
    ratio = walked["naive"]["cacheRead"] / dedup["cacheRead"] if dedup["cacheRead"] else 0
    print("Responses (deduplicated): %d, from %d usage rows" % (len(responses), walked["usageRows"]))
    print("Tokens: input %d | cache write %d | cache read %d | output %d (thinking %d)"
          % (dedup["input"], dedup["cacheWrite"], dedup["cacheRead"], dedup["output"], tokens["totals"]["thinking"]))
    print("Summing rows instead would have counted %.2f times the real cache reads" % ratio)
    print("Segments (between context resets): %d | compacts: %d" % (len(walked["segments"]), len(walked["boundaries"])))
    print("Turns: %d prompts from Marcus" % len(walked["turns"]))
    if last:
        print("Context now (last response): %d tokens. Compare with the app's context number." % tx.context_size(last[-1]))
    for key in ("C1_context", "C2_completeness", "C3_compact", "C5_claims", "C6_mutations", "privacy"):
        print("%-16s %s" % (key, "PASS" if all(c["pass"] for c in checks[key]) else "FAIL"))
    print("Test commands in the transcripts: %d recorded, %d not recorded"
          % (checks["testCommands"]["recorded"], checks["testCommands"]["unrecorded"]))
    print("All checks pass: %s" % all_pass)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
