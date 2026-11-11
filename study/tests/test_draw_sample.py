"""The sample on disk must be exactly what draw_sample.py draws from the committed frame.

Round 1 (Phase 2) must never change; round 2 (Phase 5) adds 4 per national stratum and 1 Ohio S2
school, with no school drawn twice. These tests read the committed data/frame/frame.csv and
data/frame/sample.csv, so they run in CI without the large IPEDS CSVs.
"""
import csv
from collections import Counter
from pathlib import Path

import draw_sample as ds

REPO = Path(__file__).resolve().parents[2]

# The 15 schools of round 1, in file order, as approved in specs/phase-2-study.md.
ROUND1 = [
    ("174066", "national", "random"), ("234076", "national", "random"), ("162928", "national", "random"),
    ("166683", "national", "random"), ("152600", "national", "random"), ("218539", "national", "random"),
    ("162283", "national", "random"), ("220604", "national", "random"), ("230597", "national", "random"),
    ("213659", "national", "random"), ("201885", "ohio", "fixed by Marcus"), ("204796", "ohio", "fixed by Marcus"),
    ("201195", "ohio", "random"), ("202514", "ohio", "random"), ("202222", "ohio", "random"),
]


def read(name):
    with open(REPO / "data" / "frame" / name, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_round1_rows_are_unchanged():
    rows = read("sample.csv")
    assert [(r["unitid"], r["group"], r["how"]) for r in rows[:15]] == ROUND1


def test_drawing_again_from_the_committed_frame_gives_the_committed_sample():
    frame = sorted(read("frame.csv"), key=lambda r: int(r["unitid"]))
    sample, _ = ds.draw(frame)
    expected = [{k: str(v) for k, v in r.items()} for r in sample]
    assert read("sample.csv") == expected


def test_round2_has_four_per_national_stratum_and_one_ohio_s2_school():
    rows = read("sample.csv")
    round2 = rows[15:]
    assert all(r["how"] == ds.ROUND2_HOW for r in round2)
    national = [r for r in round2 if r["group"] == "national"]
    ohio = [r for r in round2 if r["group"] == "ohio"]
    assert Counter(r["stratum"] for r in national) == {code: ds.ROUND2_PER_STRATUM for code in ds.STRATA}
    assert all(r["state"] != "OH" for r in national)
    assert [(r["state"], r["stratum"]) for r in ohio] == [("OH", "S2")]
    assert len(rows) == 36


def test_no_school_is_drawn_twice():
    ids = [r["unitid"] for r in read("sample.csv")]
    assert len(ids) == len(set(ids))


def test_how_values_contain_no_comma():
    # The web app and its tests split sample.csv lines on commas.
    assert all("," not in r["how"] for r in read("sample.csv"))
