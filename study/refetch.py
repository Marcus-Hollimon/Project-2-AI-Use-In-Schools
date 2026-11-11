"""Check R1 (specs/phase-2-study.md): fetch every archived source URL again and report what changed.

Run from the repo root:
  uv run --no-project python -I study/refetch.py

For each data/sources/<slug>/*.meta.json written by save_page.py:
- raw curl archives are fetched again with the same curl command save_page.py uses (same flags,
  same User-Agent, nothing added), into a temporary folder outside the repo, and the SHA-256 is
  compared with the saved one;
- when the bytes differ, every quote that data/coded/values.json takes from that archive is looked
  for in the new copy (same text extraction as check S1), because many web pages change bytes on
  every load (dates, tokens) while the policy text stays the same;
- a 401, 403 or 429 answer is reported as "refused", not "gone": the site blocked the request;
- rendered-text records (browser pane) have no byte hash to compare and are listed separately.

Writes data/coded/refetch-report.json and data/coded/refetch-report.md. This is a report, not a
test: policies change, and a changed page does not make the coded value wrong for the day it was
coded. The saved archives are never touched.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_study import normalize, page_text
from docx_text import docx_text
from save_page import USER_AGENT

ROOT = Path(__file__).resolve().parent.parent


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def quotes_by_archive():
    data = json.loads((ROOT / "data" / "coded" / "values.json").read_text(encoding="utf-8"))
    out = {}
    for school in data["schools"]:
        for var, v in school["values"].items():
            if v.get("archive") and v.get("quote"):
                out.setdefault(v["archive"], []).append({"variable": var, "quote": v["quote"]})
    return out


def fetch(url, dest):
    proc = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "60", "-A", USER_AGENT, "-o", str(dest),
         "-w", "%{http_code}\\n%{url_effective}\\n%{content_type}", url],
        capture_output=True, text=True, check=False)
    status, final_url, ctype = (proc.stdout.split("\n") + ["", "", ""])[:3]
    return proc.returncode, (int(status) if status.isdigit() else None), final_url, ctype, proc.stderr.strip()


def new_text(path, ctype):
    ctype = ctype.lower()
    if "pdf" in ctype:
        txt = Path(str(path) + ".txt")
        subprocess.run(["pdftotext", "-enc", "UTF-8", str(path), str(txt)], capture_output=True, check=False)
        return normalize(txt.read_text(encoding="utf-8", errors="replace")) if txt.exists() else ""
    if "wordprocessingml" in ctype:
        return normalize(docx_text(path))
    return page_text(path)


def main():
    quotes = quotes_by_archive()
    rows = []
    tmp = Path(tempfile.mkdtemp(prefix="refetch-"))
    metas = sorted((ROOT / "data" / "sources").glob("*/*.meta.json"))
    for i, meta_path in enumerate(metas):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        archive = meta_path.as_posix()[len(ROOT.as_posix()) + 1:-len(".meta.json")]
        row = {"archive": archive, "url": meta["url"], "kind": meta["kind"],
               "saved_sha256": meta["sha256"], "saved_at": meta["fetched_at"],
               "coded_quotes": len(quotes.get(archive, []))}
        if meta["kind"] != "raw bytes from curl":
            row["result"] = "rendered text (no byte hash to compare)"
            rows.append(row)
            continue
        dest = tmp / ("%03d" % i)
        code, status, final_url, ctype, err = fetch(meta["url"], dest)
        row.update({"refetched_at": now(), "http_status": status, "final_url": final_url})
        if code != 0 or not dest.exists():
            row["result"] = "gone"
            row["detail"] = "curl failed (%d): %s" % (code, err)
        elif status in (401, 403, 429):
            # A refusal says the site blocked this request, not that the page is gone. Not retried
            # with other headers (project rule); check such pages in the browser pane instead.
            row["result"] = "refused"
            row["detail"] = "HTTP %s (site refused the request; the page may still exist)" % status
        elif status is None or status >= 400:
            row["result"] = "gone"
            row["detail"] = "HTTP %s" % status
        else:
            digest = hashlib.sha256(dest.read_bytes()).hexdigest()
            row["new_sha256"] = digest
            if digest == meta["sha256"]:
                row["result"] = "unchanged"
            else:
                row["result"] = "changed"
                text = new_text(dest, ctype)
                row["quotes"] = [dict(q, still_present=normalize(q["quote"]) in text)
                                 for q in quotes.get(archive, [])]
        rows.append(row)
        print("%-9s %s" % (row["result"].split(" ")[0], archive))

    counts = {}
    for r in rows:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    lost = [(r["archive"], q["variable"]) for r in rows for q in r.get("quotes", []) if not q["still_present"]]
    report = {"generated_at": now(), "pages": len(rows), "counts": counts,
              "coded_quotes_missing_from_new_copy": len(lost), "rows": rows}
    out = ROOT / "data" / "coded"
    (out / "refetch-report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")

    md = ["# R1 re-fetch report", "",
          "Generated %s by `study/refetch.py`. Every archived source URL was fetched again with the same "
          "curl command used to save it. A report, not a failure: policies change." % report["generated_at"], "",
          "| Result | Pages |", "|---|---|"]
    md += ["| %s | %d |" % (k, v) for k, v in sorted(counts.items())]
    md += ["", "Coded quotes no longer found in the new copy of a changed page: %d." % len(lost), ""]
    for title, keep in [("Changed", "changed"), ("Refused", "refused"), ("Gone", "gone")]:
        sel = [r for r in rows if r["result"] == keep]
        if not sel:
            continue
        md += ["## %s" % title, "", "| Archive | Coded quotes | Detail |", "|---|---|---|"]
        for r in sel:
            if keep == "changed":
                qs = r.get("quotes", [])
                detail = ("all %d still present" % len(qs)) if qs and all(q["still_present"] for q in qs) else \
                    "; ".join("%s %s" % (q["variable"], "present" if q["still_present"] else "MISSING") for q in qs) \
                    or "no quotes coded from this page"
            else:
                detail = r.get("detail", "")
            md.append("| `%s` | %d | %s |" % (r["archive"], r["coded_quotes"], detail))
        md.append("")
    rendered = [r for r in rows if r["result"].startswith("rendered")]
    if rendered:
        md += ["## Rendered text (not compared)", ""] + ["- `%s`" % r["archive"] for r in rendered] + [""]
    notes = out / "refetch-notes.md"  # hand-written follow-up checks (browser pane), kept across runs
    if notes.exists():
        md += [notes.read_text(encoding="utf-8").rstrip(), ""]
    (out / "refetch-report.md").write_text("\n".join(md), encoding="utf-8")
    print("Pages %d: %s. Coded quotes missing from a changed page: %d" % (len(rows), counts, len(lost)))


if __name__ == "__main__":
    main()
