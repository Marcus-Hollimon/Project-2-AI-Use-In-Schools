"""Check the coded study data against its archived sources and the codebook.

Run from the repo root:
  uv run --no-project python -I study/check_study.py              (all 15 schools)
  uv run --no-project python -I study/check_study.py --only 174066,163286

Writes data/coded/checks.json and prints one line per school. Exit code 1 if any check fails.
Checks (defined in specs/phase-2-study.md): S1 quote in source, S2 hash, S3 fetch record,
S4 right school, S5 quote length, C1 allowed values, C2 consistency, C3 evidence fits the value,
C4 search done, N1 second search for "none found".
"""
import csv
import hashlib
import html
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ["S1", "S2", "S3", "S4", "S5", "C1", "C2", "C3", "C4", "N1"]
STANCE_TONE_PAIRS = [("univ_stance", "univ_tone"), ("dept_stance", "dept_tone")]
SEARCHED_ABSENCES = {"none found", "no public syllabus found"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


_PUNCT = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-",
                        "\u2014": "-", "\u00a0": " ", "\u2026": "..."})


def normalize(text):
    return re.sub(r"\s+", " ", html.unescape(text).translate(_PUNCT)).strip().lower()


def page_text(path):
    path = Path(path)
    raw = path.read_bytes().decode("utf-8", errors="replace")
    if path.name.endswith(".rendered.txt") or path.suffix == ".txt":
        return normalize(raw)
    parser = _Text()
    parser.feed(raw)
    return normalize(" ".join(parser.parts))


def cue_matches(quote, cue):
    q = normalize(quote)
    if cue.endswith("*"):
        return re.search(r"\b" + re.escape(cue[:-1].lower()), q) is not None
    return re.search(r"\b" + re.escape(cue.lower()) + r"\b", q) is not None


def cues_satisfied(quote, groups):
    return all(any(cue_matches(quote, c) for c in group) for group in groups)


def load_codebook(path=None):
    cb = json.loads(Path(path or ROOT / "study" / "codebook.json").read_text(encoding="utf-8"))
    for var in cb["variables"].values():
        if "same_values_as" in var:
            var["values"] = cb["variables"][var["same_values_as"]]["values"]
    return cb


def registrable_domain(webaddr):
    host = urlparse(webaddr if "//" in webaddr else "//" + webaddr).hostname or ""
    return ".".join(host.lower().split(".")[-2:])


def on_domain(url, domain):
    host = (urlparse(url).hostname or "").lower()
    return host == domain or host.endswith("." + domain)


def load_sample(path=None):
    with open(path or ROOT / "data" / "frame" / "sample.csv", encoding="utf-8", newline="") as f:
        return {r["unitid"]: r for r in csv.DictReader(f)}


def search_log_queries(path):
    """Return {query: [result lines]} from '## Search: <query>' headings and '- ' lines under them."""
    out, current = {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"##\s*Search:\s*(.+?)\s*$", line)
        if m:
            current = m.group(1)
            out[current] = []
        elif current and line.strip().startswith("- "):
            out[current].append(line.strip()[2:])
    return out


def check_school(school, sample_row, codebook, root=ROOT):
    """Return a list of findings: {check, variable, ok, message}."""
    findings = []

    def add(check, ok, message, variable=None):
        findings.append({"check": check, "variable": variable, "ok": bool(ok), "message": message})

    domain = registrable_domain(sample_row["website"])
    values = school.get("values", {})
    absences = set(codebook["absence_values"])
    slug = school["slug"]
    log_path = root / "data" / "sources" / slug / "search-log.md"
    log = search_log_queries(log_path) if log_path.exists() else None

    # C4: the fixed search was done and logged.
    if log is None:
        add("C4", False, "no search log at data/sources/%s/search-log.md" % slug)
    else:
        for q in codebook["required_searches"]:
            q = q.format(domain=domain)
            add("C4", q in log and len(log[q]) > 0,
                "search logged with results: %s" % q if q in log and log[q] else "missing or empty: %s" % q)

    for var, spec in codebook["variables"].items():
        entry = values.get(var)
        # C1: present and allowed.
        if not entry or "value" not in entry:
            add("C1", False, "not coded", var)
            continue
        value = entry["value"]
        add("C1", value in spec["values"], "value '%s' %s" % (value, "allowed" if value in spec["values"] else "NOT in codebook"), var)
        if value not in spec["values"]:
            continue

        if value in absences:
            reviewed = entry.get("reviewed") or []
            missing = [p for p in reviewed if not (root / p).exists()]
            has_log = bool(entry.get("search_log")) and (root / entry["search_log"]).exists()
            add("C2", (reviewed and not missing) or has_log,
                "absence backed by %s" % ("%d reviewed pages" % len(reviewed) if reviewed and not missing else
                                         "search log" if has_log else "nothing (or missing files: %s)" % missing), var)
            if value in SEARCHED_ABSENCES:
                ok = log is not None and all(q.format(domain=domain) in log and log[q.format(domain=domain)]
                                             for q in codebook["second_searches"])
                add("N1", ok, "second searches %s" % ("logged" if ok else "MISSING"), var)
            continue

        # Values with evidence.
        quote, url, archive = entry.get("quote"), entry.get("url"), entry.get("archive")
        add("C2", bool(quote and url and archive), "quote, url and archive present" if quote and url and archive
            else "missing quote, url or archive", var)
        if not (quote and url and archive):
            continue
        st = entry.get("source_type")
        add("C1", st in codebook["source_types"], "source_type '%s' %s" % (st, "allowed" if st in codebook["source_types"] else "NOT allowed"), var)
        words = len(quote.split())
        add("S5", words <= codebook["max_quote_words"], "quote has %d words" % words, var)

        apath = root / archive
        meta_path = Path(str(apath) + ".meta.json")
        if not apath.exists() or not meta_path.exists():
            add("S1", False, "archive or its fetch record missing: %s" % archive, var)
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        text_path = apath
        # PDF and Word archives are binary: S1 searches the extracted text saved beside them
        # (<archive>.txt); S2 still hashes the original file.
        if apath.suffix in (".pdf", ".docx"):
            text_path = Path(str(apath) + ".txt")
        if not text_path.exists():
            add("S1", False, "no text to search for %s (PDF or Word file without extracted text)" % archive, var)
        else:
            found = normalize(quote) in page_text(text_path)
            add("S1", found, "quote %s in %s" % ("found" if found else "NOT found", archive), var)

        digest = hashlib.sha256(apath.read_bytes()).hexdigest()
        add("S2", digest == meta.get("sha256"), "hash %s" % ("matches" if digest == meta.get("sha256") else "CHANGED since saved"), var)

        if "rendered" in meta.get("kind", ""):
            # Rendered text needs a raw curl copy of the same URL: HTTP 200 (the page builds its text
            # with JavaScript), or HTTP 403 plus a written fetch_reason (the site blocks curl but
            # serves the page to a browser). Any other status fails.
            raw_statuses = set()
            for other in apath.parent.glob("*.meta.json"):
                m = json.loads(other.read_text(encoding="utf-8"))
                if m.get("url") == meta.get("url") and "raw" in m.get("kind", ""):
                    raw_statuses.add(m.get("http_status"))
            if 200 in raw_statuses:
                add("S3", True, "rendered text; raw curl copy of same URL with HTTP 200 present", var)
            elif 403 in raw_statuses:
                reason = entry.get("fetch_reason")
                add("S3", bool(reason), "rendered text; raw curl copy got HTTP 403; reason: %s" % reason, var)
            else:
                add("S3", False, "rendered text; raw curl copy of same URL with HTTP 200 (or 403 plus reason) MISSING", var)
        else:
            add("S3", meta.get("http_status") == 200, "HTTP status %s" % meta.get("http_status"), var)

        final = meta.get("final_url") or url
        ok = on_domain(final, domain) or bool(entry.get("domain_reason"))
        add("S4", ok, "%s %s %s" % (urlparse(final).hostname, "is on" if on_domain(final, domain) else "is OFF", domain)
            + ("" if on_domain(final, domain) else "; reason: %s" % entry.get("domain_reason")), var)

        groups = spec["values"][value]
        if groups:
            ok = cues_satisfied(quote, groups) or bool(entry.get("cue_reason"))
            add("C3", ok, "cue words %s" % ("present" if cues_satisfied(quote, groups) else
                                            "absent; reason: %s" % entry.get("cue_reason")), var)

    for stance, tone in STANCE_TONE_PAIRS:
        s, t = (values.get(stance) or {}).get("value"), (values.get(tone) or {}).get("value")
        if s is not None and t is not None:
            add("C2", (s == "none found") == (t == "none found"), "%s='%s' and %s='%s' agree on none found" % (stance, s, tone, t))
    return findings


def run(only=None, root=ROOT):
    codebook = load_codebook(root / "study" / "codebook.json")
    sample = load_sample(root / "data" / "frame" / "sample.csv")
    values_path = root / "data" / "coded" / "values.json"
    coded = json.loads(values_path.read_text(encoding="utf-8")) if values_path.exists() else {"schools": []}
    by_id = {s["unitid"]: s for s in coded["schools"]}
    targets = only or list(sample)
    report = {"generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
              "codebookVersion": codebook["version"], "schools": []}
    all_ok = True
    for uid in targets:
        row = sample[uid]
        school = by_id.get(uid)
        if school is None:
            findings = [{"check": "C1", "variable": None, "ok": False, "message": "school not coded yet"}]
        else:
            findings = check_school(school, row, codebook, root)
        per_check = {c: all(f["ok"] for f in findings if f["check"] == c) for c in CHECKS
                     if any(f["check"] == c for f in findings)}
        ok = all(f["ok"] for f in findings)
        all_ok &= ok
        report["schools"].append({"unitid": uid, "name": row["name"], "pass": ok, "checks": per_check, "findings": findings})
    report["pass"] = all_ok
    return report


def main(argv):
    only = None
    if argv[:1] == ["--only"]:
        only = argv[1].split(",")
    report = run(only)
    out = ROOT / "data" / "coded" / "checks.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for s in report["schools"]:
        fails = [f for f in s["findings"] if not f["ok"]]
        print("%-4s %-45s %s" % ("PASS" if s["pass"] else "FAIL", s["name"][:45],
                                 " ".join("%s:%s" % (c, "ok" if v else "FAIL") for c, v in s["checks"].items())))
        for f in fails:
            print("       %s %s: %s" % (f["check"], f["variable"] or "-", f["message"]))
    print("All checks pass:", report["pass"])
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
