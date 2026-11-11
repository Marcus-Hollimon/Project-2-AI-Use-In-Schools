"""Tests on small made-up transcripts. Each test plants one trap measured in the real data."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build  # noqa: E402
import transcripts as tx  # noqa: E402

BS = chr(92)
_counter = [0]


def uid():
    _counter[0] += 1
    return "u%d" % _counter[0]


def usage(inp=2, cw=100, cr=1000, out=50, thinking=10):
    return {"input_tokens": inp, "cache_creation_input_tokens": cw, "cache_read_input_tokens": cr,
            "output_tokens": out, "output_tokens_details": {"thinking_tokens": thinking}}


def request(t):
    return {"type": "api-request", "id": uid(), "timestamp": t}


def assistant_rows(mid, t, blocks, u=None):
    """One API response saved as one row per content block, each repeating the same usage."""
    u = u or usage()
    return [{"type": "assistant", "uuid": uid(), "timestamp": t,
             "message": {"id": mid, "model": "test-model", "usage": u, "content": [b]}} for b in blocks]


def prompt(t, text, images=0):
    content = [{"type": "image"}] * images + [{"type": "text", "text": text}]
    return {"type": "user", "uuid": uid(), "timestamp": t, "origin": {"kind": "human"}, "promptId": uid(),
            "message": {"role": "user", "content": content if images else text}}


def text(s):
    return {"type": "text", "text": s}


def tool(name="Bash", tid=None):
    return {"type": "tool_use", "id": tid or uid(), "name": name, "input": {}}


def one_file(rows, session="s1", subagent=False):
    return {"session": session, "subagent": subagent, "rows": rows}


def test_repeated_rows_of_one_response_count_once():
    rows = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("a"), tool(), tool()])
    w = tx.walk([one_file(rows)])
    assert len(w["responses"]) == 1
    assert w["responses"][0]["cacheRead"] == 1000
    assert w["naive"]["cacheRead"] == 3000
    assert w["usageRows"] == 3


def test_response_copied_into_a_resumed_file_counts_once():
    original = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z")]
    original += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("a")])
    resumed = [dict(r) for r in original]  # a resume copies the records, uuids included
    resumed += [prompt("2026-11-08T06:00:00Z", "again"), request("2026-11-08T06:00:01Z")]
    resumed += assistant_rows("m2", "2026-11-08T06:00:02Z", [text("b")])
    w = tx.walk([one_file(original, "s1"), one_file(resumed, "s2")])
    assert [r["id"] for r in w["responses"]] == ["m1", "m2"]
    assert [t["text"] for t in w["turns"]] == ["hi", "again"]  # copied prompt not duplicated
    assert w["segments"][-1]["startReason"] == "resume"


def test_compact_boundary_starts_a_segment_and_matches_tokens_before():
    u = usage(inp=2, cw=190, cr=304146, out=727)
    rows = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("a")], u)
    rows.append({"type": "system", "subtype": "compact_boundary", "uuid": uid(), "timestamp": "2026-11-08T05:05:00Z",
                 "compactMetadata": {"trigger": "manual", "preTokens": 305065, "postTokens": 14969, "durationMs": 56517}})
    rows.append({"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:05:00Z", "isCompactSummary": True,
                 "message": {"content": "This session is being continued"}})
    rows += [prompt("2026-11-08T05:06:00Z", "continue"), request("2026-11-08T05:06:01Z")]
    rows += assistant_rows("m2", "2026-11-08T05:06:02Z", [text("b")])
    w = tx.walk([one_file(rows)])
    assert len(w["segments"]) == 2
    assert w["segments"][0]["endReason"] == "/compact"
    assert [r["segment"] for r in w["responses"]] == [1, 2]
    assert tx.check_compacts(w["boundaries"])[0]["pass"]
    assert [t["text"] for t in w["turns"]] == ["hi", "continue"]  # the summary is not a prompt


def test_compact_check_fails_when_tokens_disagree():
    boundary = {"time": "t", "preTokens": 100, "lastResponseContextPlusOutput": 99}
    assert not tx.check_compacts([boundary])[0]["pass"]


def test_request_in_flight_is_allowed_only_for_the_live_session():
    rows = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("a")])
    rows.append(request("2026-11-08T05:00:10Z"))
    w = tx.walk([one_file(rows, "live")])
    assert tx.check_completeness(w["fileStats"], "live")[0]["pass"]
    assert not tx.check_completeness(w["fileStats"], "other")[0]["pass"]


def test_unanswered_retry_is_listed_and_unexplained_gaps_fail():
    rows = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z"), request("2026-11-08T05:00:02Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:03Z", [text("a")])
    w = tx.walk([one_file(rows, "old")])
    assert w["fileStats"][0]["unansweredRequests"] == ["2026-11-08T05:00:01Z"]
    assert tx.check_completeness(w["fileStats"], "live")[0]["pass"]
    broken = dict(w["fileStats"][0], apiRequests=5)
    assert not tx.check_completeness([broken], "live")[0]["pass"]


def test_user_records_that_are_not_prompts():
    ask = tool("AskUserQuestion", "ask1")
    rows = [prompt("2026-11-08T05:00:00Z", "real question"), request("2026-11-08T05:00:01Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:02Z", [ask, tool(tid="b1")])
    rows += [
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:03Z",
         "message": {"content": [{"type": "tool_result", "tool_use_id": "b1", "content": "secret file text"}]}},
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:04Z",
         "message": {"content": [{"type": "tool_result", "tool_use_id": "ask1", "content": "Marcus picked A"}]}},
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:05Z", "isMeta": True,
         "message": {"content": "<local-command-caveat>caveat</local-command-caveat>"}},
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:05Z",
         "message": {"content": "<command-name>/model</command-name> <command-args>opus</command-args>"}},
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:06Z",
         "message": {"content": "<local-command-stdout>Set model</local-command-stdout>"}},
        {"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:07Z", "isMeta": True, "origin": {"kind": "human"},
         "message": {"content": [{"type": "text", "text": "[Image: source: C:/x.png]"}]}},
        {"type": "attachment", "uuid": uid(), "timestamp": "2026-11-08T05:00:08Z", "attachment": {"type": "hook"}},
    ]
    w = tx.walk([one_file(rows)])
    assert [t["text"] for t in w["turns"]] == ["real question"]
    assert w["turns"][0]["toolCalls"] == 2
    kinds = {(e["kind"], e["text"]) for e in w["events"]}
    assert kinds == {("answer", "Marcus picked A"), ("command", "/model opus")}
    assert "secret file text" not in repr(w)


def test_reply_is_the_last_text_response_of_the_turn_and_images_are_counted():
    rows = [prompt("2026-11-08T05:00:00Z", "look", images=2), request("2026-11-08T05:00:01Z")]
    rows += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("working on it"), tool()])
    rows += [request("2026-11-08T05:00:05Z")] + assistant_rows("m2", "2026-11-08T05:00:06Z", [text("final"), text("answer")])
    w = tx.walk([one_file(rows)])
    assert w["turns"][0]["images"] == 2
    assert w["turns"][0]["reply"] == "final\n\nanswer"


def test_subagent_files_add_tokens_but_never_prompts():
    main = [prompt("2026-11-08T05:00:00Z", "hi"), request("2026-11-08T05:00:01Z")]
    main += assistant_rows("m1", "2026-11-08T05:00:02Z", [text("a")])
    sub = [{"type": "user", "uuid": uid(), "timestamp": "2026-11-08T05:00:03Z", "origin": {"kind": "human"},
            "message": {"content": "task for subagent"}}, request("2026-11-08T05:00:03Z")]
    sub += assistant_rows("m9", "2026-11-08T05:00:04Z", [text("sub reply")])
    w = tx.walk([one_file(main), one_file(sub, subagent=True)])
    assert [r["id"] for r in w["responses"]] == ["m1", "m9"]
    assert w["responses"][1]["subagent"] is True
    assert len(w["turns"]) == 1 and w["turns"][0]["reply"] == "a"


def test_phase_is_the_latest_reading_at_or_before_the_response():
    readings = [{"time": "2026-11-08T05:28:00Z", "phase": "0"}, {"time": "2026-11-08T05:57:55Z", "phase": "1"}]
    responses = [{"time": t} for t in ("2026-11-08T05:10:00Z", "2026-11-08T05:28:00Z", "2026-11-08T06:00:00Z")]
    assert [r["phase"] for r in tx.assign_phases(responses, readings)] == ["planning", "0", "1"]


def test_context_check_needs_the_reading_between_two_consecutive_responses_in_time():
    # Real values from 2026-11-11 14:52: the app read 224,386 while the response at 14:52:03 ran.
    r = [{"time": "2026-11-11T14:52:03Z", "input": 2, "cacheWrite": 0, "cacheRead": 222905, "output": 2312},
         {"time": "2026-11-11T14:52:23Z", "input": 2, "cacheWrite": 0, "cacheRead": 226002, "output": 577}]
    assert tx.check_context([{"time": "2026-11-11T14:52:00Z", "context": 224386}], r)[0]["pass"]
    assert tx.check_context([{"time": "2026-11-11T14:52:00Z", "context": 222907}], r)[0]["pass"]  # edge counts
    assert tx.check_context([{"time": "2026-11-11T14:52:00Z", "context": 230000}], r)[0]["pass"] is False
    assert tx.check_context([{"time": "2026-11-11T14:52:00Z", "context": 200000}], r)[0]["pass"] is False
    assert tx.check_context([{"time": "2026-11-11T15:30:00Z", "context": 224386}], r)[0]["pass"] is False


def test_scrubber_removes_home_folder_in_every_spelling_and_the_email(monkeypatch):
    home = BS.join(["C:", "Users", "testuser"])
    monkeypatch.setattr(build.os.path, "expanduser", lambda p: home if p == "~" else p)
    monkeypatch.setattr(build, "git_email", lambda: "someone@example.com")
    scrub, leaks = build.make_scrubber()
    samples = [home + BS + "x.txt", "C:/Users/testuser/x", "/c/Users/testuser/x",
               (BS * 2).join(["C:", "Users", "testuser"]), "c:" + BS + "users" + BS + "TESTUSER", "mail someone@example.com"]
    cleaned = [scrub(s) for s in samples]
    assert all("testuser" not in c.lower() and "someone@" not in c for c in cleaned), cleaned
    assert cleaned[1] == "~/x"


def test_usage_row_with_missing_columns_stops_the_build():
    # Trap measured 2026-11-11: seven readings written with 5 cells (no Phase, no reset column)
    # were read with every value shifted one column, and nothing failed.
    good = ["2026-11-11T11:33:07-05:00", "2", "phase end", "71", "17", "118,314", "none"]
    assert build.parse_readings([good])[0]["context"] == 118314
    short = ["2026-11-11T11:24:12-05:00", "main coding done", "66", "16", "195,190"]
    for bad in (short, good[:1] + ["main coding done"] + good[2:], good[:3] + ["16%"] + good[4:]):
        try:
            build.parse_readings([bad])
        except ValueError as err:
            assert "usage.md row" in str(err)
        else:
            raise AssertionError("malformed row was accepted: %r" % (bad,))
