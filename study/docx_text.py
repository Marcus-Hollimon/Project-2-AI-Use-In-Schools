"""Extract the text of a saved Word (.docx) archive into <archive>.txt, one paragraph per line.

check_study.py searches that .txt for quotes (check S1), the same way it uses pdftotext output for
PDFs. Standard library only.

    uv run --no-project python -I study/docx_text.py data/sources/<slug>/<file>.docx
"""
import html
import re
import sys
import zipfile
from pathlib import Path


def docx_text(path):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    paragraphs = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S)
    lines = []
    for p in paragraphs:
        p = re.sub(r"<w:tab/>", " ", p)
        lines.append(html.unescape(re.sub(r"<[^>]+>", "", p)))
    return "\n".join(lines) + "\n"


def main():
    src = Path(sys.argv[1])
    out = Path(str(src) + ".txt")
    out.write_text(docx_text(src), encoding="utf-8")
    print("Wrote %s (%d words)" % (out, len(out.read_text(encoding="utf-8").split())))


if __name__ == "__main__":
    main()
