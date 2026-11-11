"""Build the sampling frame from IPEDS 2024 and draw the study sample.

Round 1 (Phase 2): 15 schools, seed SEED. Round 2 (Phase 5, specs/phase-5-more-schools.md): 21 more,
seed SEED_ROUND2, drawn after round 1 from its own generator, so round 1 is unchanged.

Run from the repo root:  uv run --no-project python -I study/draw_sample.py
Reads data/frame/extracted/HD2024.csv and C2024_a.csv (unzipped from the archived IPEDS zips).
Writes data/frame/frame.csv (every eligible school with its stratum) and data/frame/sample.csv.
Standard library only. Each seed was committed before its first run (round 2: pushed to GitHub too).
"""
import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20261111
SEED_ROUND2 = 20261115  # named in specs/phase-5-more-schools.md, pushed before the first run
ROUND2_PER_STRATUM = 4
ROUND2_HOW = "random round 2"  # no comma: the web app and tests split sample.csv lines on commas
ROOT = Path(__file__).resolve().parent.parent
FRAME_DIR = ROOT / "data" / "frame"
SRC = FRAME_DIR / "extracted"

# Frame: a degree (associate's 3, bachelor's 5, master's 7, research doctorate 17), first major,
# in Computer Science (11.0701) or Computer and Information Sciences, General (11.0101).
CS_CIPS = {"11.0701", "11.0101"}
DEGREE_LEVELS = {"3", "5", "7", "17"}

FIXED_OHIO = {"204796": "Ohio State University-Main Campus", "201885": "University of Cincinnati-Main Campus"}
# Branch campuses of the two fixed schools share their parent's policies, so they are not drawn.
FIXED_BRANCH_PREFIXES = ("Ohio State University-", "University of Cincinnati-")

STRATA = {
    "S1": "Public R1 universities",
    "S2": "Private R1 universities",
    "S3": "Other universities with graduate programs",
    "S4": "Baccalaureate colleges",
    "S5": "Associate's colleges",
}
# 2025 Carnegie Institutional Classification codes by degree level (labels in HD2024_dict.xlsx).
IC_GRADUATE = {6, 7, 8, 9, 10, 16, 17, 18, 19, 20}  # "Undergraduate/Graduate"
IC_BACCALAUREATE = {5, 14, 15}  # "Baccalaureate"
IC_ASSOCIATE = {1, 2, 3, 4, 11, 12, 13}  # "Associate" and "Associate/Baccalaureate"
# Special Focus (21 to 31) and Not classified (-2) carry no degree level; HLOFFER decides instead.


def stratum(row):
    control, rsch, ic, hl = row["CONTROL"], row["CARNEGIERSCH"], int(row["CARNEGIEIC"]), int(row["HLOFFER"])
    if rsch == "1":
        return "S1" if control == "1" else "S2"
    if ic in IC_GRADUATE:
        return "S3"
    if ic in IC_BACCALAUREATE:
        return "S4"
    if ic in IC_ASSOCIATE:
        return "S5"
    if hl >= 6:
        return "S3"
    if hl == 5:
        return "S4"
    return "S5"


def draw_round2(national, ohio, already):
    """Round 2: 4 more per national stratum, then 1 Ohio school from S2 (private R1, the only Ohio
    type with no school in round 1). Schools already drawn are left out of every pool."""
    rng = random.Random(SEED_ROUND2)
    out = []
    for code in STRATA:  # fixed order S1..S5
        pool = [s for s in national[code] if s["unitid"] not in already]
        for s in rng.sample(pool, ROUND2_PER_STRATUM):
            out.append(dict(s, group="national", how=ROUND2_HOW))
    pool = [s for s in ohio["S2"] if s["unitid"] not in already]
    out.append(dict(rng.sample(pool, 1)[0], group="ohio", how=ROUND2_HOW))
    return out


def main():
    awards = Counter()
    with open(SRC / "C2024_a.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["CIPCODE"] in CS_CIPS and r["MAJORNUM"] == "1" and r["AWLEVEL"] in DEGREE_LEVELS:
                n = int(r["CTOTALT"] or 0)
                if n > 0:
                    awards[r["UNITID"]] += n

    frame, excluded = [], Counter()
    with open(SRC / "HD2024.csv", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f)
        id_col = reader.fieldnames[0]  # "UNITID", possibly with a byte-order mark
        for r in reader:
            uid = r[id_col]
            if uid not in awards:
                continue
            if r["CONTROL"] == "3":
                excluded["private for-profit"] += 1
                continue
            if r["OBEREG"] == "9":
                excluded["outlying territory"] += 1
                continue
            if r["CYACTIVE"] != "1" or r["DEGGRANT"] != "1":
                excluded["inactive or not degree-granting"] += 1
                continue
            frame.append({
                "unitid": uid, "name": r["INSTNM"], "state": r["STABBR"], "region": r["OBEREG"],
                "control": r["CONTROL"], "carnegie_research": r["CARNEGIERSCH"],
                "carnegie_ic": r["CARNEGIEIC"], "highest_offering": r["HLOFFER"],
                "website": r["WEBADDR"], "cs_degrees_2024": awards[uid], "stratum": stratum(r),
            })
    frame.sort(key=lambda x: int(x["unitid"]))

    sample, national = draw(frame)
    write_and_report(frame, sample, national, awards, excluded)


def pools(frame):
    """National pools by stratum (Ohio left out) and Ohio pools (fixed schools and their branches left out)."""
    national, ohio = defaultdict(list), defaultdict(list)
    for s in frame:
        if s["state"] == "OH":
            if s["unitid"] not in FIXED_OHIO and not s["name"].startswith(FIXED_BRANCH_PREFIXES):
                ohio[s["stratum"]].append(s)
        else:
            national[s["stratum"]].append(s)
    return national, ohio


def draw(frame):
    """Round 1 then round 2, from a frame sorted by unitid. Returns (sample rows, national pools)."""
    rng = random.Random(SEED)
    sample = []
    national, ohio = pools(frame)
    for code in STRATA:  # fixed order S1..S5, so the random stream is reproducible
        for s in rng.sample(national[code], 2):
            sample.append(dict(s, group="national", how="random"))
    for s in frame:
        if s["unitid"] in FIXED_OHIO:
            sample.append(dict(s, group="ohio", how="fixed by Marcus"))
    for code in ("S3", "S4", "S5"):
        s = rng.sample(ohio[code], 1)[0]
        sample.append(dict(s, group="ohio", how="random"))
    sample += draw_round2(national, ohio, {s["unitid"] for s in sample})
    return sample, national


def write_and_report(frame, sample, national, awards, excluded):
    fields = list(frame[0].keys())
    with open(FRAME_DIR / "frame.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(frame)
    with open(FRAME_DIR / "sample.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["group", "how"] + fields)
        w.writeheader()
        w.writerows(sample)

    print("Seeds: round 1", SEED, "round 2", SEED_ROUND2)
    print("Schools awarding a CS degree (11.0701 or 11.0101):", len(awards))
    print("Excluded:", dict(excluded))
    print("Frame:", len(frame))
    for code, label in STRATA.items():
        print("  %s %-45s national %4d  Ohio %3d" % (code, label, len(national[code]),
              sum(1 for s in frame if s["state"] == "OH" and s["stratum"] == code)))
    print("Sample:")
    for s in sample:
        print("  %-8s %-16s %s %-55s %s region %s, %s CS degrees" % (
            s["group"], s["how"], s["stratum"], s["name"], s["state"], s["region"], s["cs_degrees_2024"]))


if __name__ == "__main__":
    main()
