"""Run the pipeline tests and save the run to validation/runs/<time>_pipeline.json.

Same top-level shape as the web runs (web/scripts/record-tests.mjs), and the report uses the same
testResults/assertionResults layout, so the Validation tab reads both suites one way.

Run from the repo root:  uv run --project pipeline python pipeline/record_tests.py "optional label"
Study checks (Phase 2): uv run --project pipeline python pipeline/record_tests.py --suite study "optional label"
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def current_phase():
    for line in open(os.path.join(ROOT, "progress", "STATE.md"), encoding="utf-8"):
        m = re.match(r"Current phase: (\d+)", line)
        if m:
            return int(m.group(1))
    return None


def main():
    args = sys.argv[1:]
    suite = "pipeline"
    if args[:1] == ["--suite"]:
        suite, args = args[1], args[2:]
    if suite not in ("pipeline", "study"):
        sys.exit("unknown suite: %s" % suite)
    label = " ".join(args) or None
    xml_path = os.path.join(tempfile.mkdtemp(), suite + "-junit.xml")
    started = now()
    if suite == "pipeline":
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "--junit-xml=" + xml_path], cwd=HERE)
    else:
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "study/tests", "--junit-xml=" + xml_path], cwd=ROOT)
    finished = now()

    files = {}
    counts = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    for case in ET.parse(xml_path).getroot().iter("testcase"):
        failure = case.find("failure")
        if failure is None:
            failure = case.find("error")
        if failure is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        counts["total"] += 1
        counts[status] += 1
        module = case.get("classname", "")
        if suite == "pipeline":
            name = "pipeline/" + module.replace(".", "/") + ".py"
        else:
            name = "study/tests/" + module.split(".")[-1] + ".py"
        files.setdefault(name, []).append({
            "ancestorTitles": [module], "fullName": module + " " + case.get("name"), "title": case.get("name"),
            "status": status, "duration": round(float(case.get("time", 0)) * 1000, 3),
            "failureMessages": [failure.get("message") or ""] if failure is not None else [],
        })

    run = {
        "suite": suite, "runner": "pytest",
        "command": "uv run --project pipeline python pipeline/record_tests.py" + ("" if suite == "pipeline" else " --suite study"),
        "label": label, "startedAt": started, "finishedAt": finished, "phase": current_phase(),
        "gitCommit": git("rev-parse", "--short", "HEAD"), "uncommittedChanges": bool(git("status", "--porcelain")),
        "exitCode": proc.returncode, "summary": counts,
        "report": {"testResults": [{"name": n, "status": "failed" if any(a["status"] == "failed" for a in a_list) else "passed",
                                    "assertionResults": a_list} for n, a_list in files.items()]},
    }
    out_dir = os.path.join(ROOT, "validation", "runs")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, started.replace(":", "-").replace(".", "-") + "_" + suite + ".json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(run, fh, indent=1)
        fh.write("\n")
    print("Recorded %s: %d passed, %d failed, %d skipped" % (os.path.relpath(out, ROOT).replace(os.sep, "/"),
                                                           counts["passed"], counts["failed"], counts["skipped"]))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
