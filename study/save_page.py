"""Archive one source page with curl and write its fetch record (checks S2 and S3 rely on it).

Run from the repo root:
  uv run --no-project python -I study/save_page.py <slug> <name> <url>
  uv run --no-project python -I study/save_page.py --rendered <slug> <name> <url> <text-file>

The first form saves the real bytes curl receives as data/sources/<slug>/<date>-<name>.<ext>.
The second is for pages that build their text with JavaScript: it files text taken from Claude's
browser pane as <date>-<name>.rendered.txt, recording that it is rendered text, not raw bytes.
Each archive gets <archive>.meta.json: URL requested, final URL, HTTP status, time, size, SHA-256.
Existing archives are never overwritten.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def target(slug, name, ext):
    folder = ROOT / "data" / "sources" / slug
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / ("%s-%s.%s" % (datetime.now().strftime("%Y-%m-%d"), name, ext))
    if path.exists():
        sys.exit("Refusing to overwrite %s" % path.relative_to(ROOT).as_posix())
    return path


def write_meta(path, meta):
    meta.update({"sha256": sha256(path), "bytes": path.stat().st_size})
    Path(str(path) + ".meta.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print("Saved %s (%d bytes, HTTP %s, final URL %s)" % (
        path.relative_to(ROOT).as_posix(), meta["bytes"], meta.get("http_status"), meta.get("final_url")))


def fetch(slug, name, url):
    tmp = Path(tempfile.mkdtemp()) / "page"
    fetched_at = now()
    proc = subprocess.run(
        ["curl", "-sS", "-L", "--max-time", "60", "-A", USER_AGENT, "-o", str(tmp),
         "-w", "%{http_code}\\n%{url_effective}\\n%{content_type}", url],
        capture_output=True, text=True)
    if proc.returncode != 0 or not tmp.exists():
        sys.exit("curl failed (%d): %s" % (proc.returncode, proc.stderr.strip()))
    status, final_url, content_type = (proc.stdout.split("\n") + ["", "", ""])[:3]
    ext = "pdf" if "pdf" in content_type.lower() else "html"
    path = target(slug, name, ext)
    shutil.move(str(tmp), path)
    write_meta(path, {"kind": "raw bytes from curl", "url": url, "final_url": final_url,
                      "http_status": int(status) if status.isdigit() else status,
                      "content_type": content_type, "fetched_at": fetched_at})


def file_rendered(slug, name, url, text_file):
    path = target(slug, name, "rendered.txt")
    shutil.copyfile(text_file, path)
    # No HTTP status is measured on this path, so none is claimed. Check S3 instead requires a raw
    # curl archive of the same URL in the same folder (proof the page answered with 200).
    write_meta(path, {"kind": "rendered text from Claude's browser pane", "url": url, "final_url": url,
                      "http_status": None, "content_type": "text/plain", "fetched_at": now()})


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--rendered"] and len(args) == 5:
        file_rendered(*args[1:])
    elif len(args) == 3:
        fetch(*args)
    else:
        sys.exit(__doc__)
