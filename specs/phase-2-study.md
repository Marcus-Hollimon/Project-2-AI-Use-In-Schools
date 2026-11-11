# Phase 2: Study (15 schools)

Goal: find, archive, and code what 15 US computer science departments (and their universities)
publicly say about generative AI, so the Research findings tab (deliverable 1) has data in which
every value can be checked against a saved copy of its source.

Status: DRAFT, waiting for Marcus's approval (written 2026-11-11 by Claude, session a9056776).
Nothing below "Tasks" has started. The frame and the draw are done, because the approval covers
the drawn list too.

## Known before any coding (measured 2026-11-11)
Raw files: `data/frame/*.zip`, downloaded 10:03 EST from `https://nces.ed.gov/ipeds/datacenter/data/`
(`HD2024.zip`, `C2024_A.zip`, and their `_Dict` files). SHA-256 in `data/frame/SOURCES.md`.
1. **2024 is the newest IPEDS year** the site serves (`HD2025.zip` and `C2025_A.zip` return 404).
   The completions file covers degrees awarded July 2023 to June 2024.
2. **The 2024 files carry the new 2025 Carnegie classification**, read from the dictionary:
   `CARNEGIERSCH` (research designation: R1, R2, research colleges) and `CARNEGIEIC` (31
   institutional classes). The old scheme survives as `C21BASIC`. We use the 2025 fields because
   they are current. The 2025 classes group schools by **the mix of degrees they award**, not the
   highest degree they offer: Coppin State offers doctorates but awards mostly bachelor's, so it
   is "Baccalaureate". Strata labels below say "mostly" for that reason.
3. **A frame built on CIP 11.0701 (Computer Science) alone would have excluded both required
   schools.** That was the plan in STATE.md, written by Claude before the /clear; it was wrong.
   Ohio State reports its CS degrees as 11.0101 (Computer and Information Sciences, General) and
   14.0901 (Computer Engineering); Cincinnati as 11.0101 and 11.0103. Fix: the frame uses 11.0701
   **or** 11.0101. Both required schools now enter on the same rule as everyone else.
4. Liberal arts colleges (Pomona, Occidental) and engineering schools (Caltech, Harvey Mudd) sit
   in 2025 "Special Focus" classes that carry no degree level. Rule: R1 status is checked first;
   then special-focus and unclassified schools go by highest degree offered (`HLOFFER`).

## Frame and strata (as built by `study/draw_sample.py`)
Frame: active, degree-granting, public or private nonprofit institutions in the 50 states and DC
that awarded at least one associate's, bachelor's, master's, or research doctorate in CIP 11.0701
or 11.0101 (first major), 2023 to 2024. Excluded: 28 for-profit, 24 in outlying territories.

| Stratum | Who | National | Ohio |
|---|---|---|---|
| S1 | Public R1 universities | 121 | 5 |
| S2 | Private nonprofit R1 universities | 48 | 2 |
| S3 | Other four-year schools awarding many graduate degrees | 629 | 24 |
| S4 | Four-year schools awarding mostly bachelor's degrees | 251 | 11 |
| S5 | Schools awarding mostly associate's degrees (community colleges) | 412 | 6 |
| | Total frame: 1,509 | 1,461 | 48 |

## The drawn sample (seed 20261111, committed in `405f8dd` before the first run)
National: 2 per stratum at random, Ohio excluded. Ohio: the two fixed schools, plus 1 at random
from each of S3, S4, S5 (branch campuses of Ohio State and Cincinnati excluded). A second run
reproduced both output files byte for byte.

| # | Group | Stratum | School | State | How chosen |
|---|---|---|---|---|---|
| 1 | National | S1 | University of Minnesota-Twin Cities | MN | random |
| 2 | National | S1 | University of Virginia | VA | random |
| 3 | National | S2 | Johns Hopkins University | MD | random |
| 4 | National | S2 | Massachusetts Institute of Technology | MA | random |
| 5 | National | S3 | Valparaiso University | IN | random |
| 6 | National | S3 | Presbyterian College | SC | random |
| 7 | National | S4 | Coppin State University | MD | random |
| 8 | National | S4 | Le Moyne-Owen College | TN | random |
| 9 | National | S5 | Snow College | UT | random |
| 10 | National | S5 | Luzerne County Community College | PA | random |
| 11 | Ohio | S1 | University of Cincinnati | OH | fixed by Marcus |
| 12 | Ohio | S1 | Ohio State University | OH | fixed by Marcus |
| 13 | Ohio | S3 | Baldwin Wallace University | OH | random |
| 14 | Ohio | S4 | Defiance College | OH | random |
| 15 | Ohio | S5 | Columbus State Community College | OH | random |

Worth knowing before approving:
- Harvard was not drawn. Private R1 got MIT and Johns Hopkins. Adding Harvard by hand would make
  that stratum a chosen pick again.
- Four schools award under 10 CS degrees a year (Presbyterian 7, Coppin State 8, Le Moyne-Owen 3,
  Defiance 3). Small programs may publish nothing about AI. "None found" is a real finding, as
  long as the search behind it is the same fixed search every school gets (below).
- With 2 schools per stratum the results are **illustrative, not estimates**. National 10 are
  reported by stratum; Ohio 5 separately; never pooled into one "US" percentage. The site says so.

## Codebook (version 1; frozen before the first school is coded)
Two levels are coded separately for every school, because they often disagree: the **university**
(provost, teaching center, academic integrity office) and the **CS department** (department pages,
handbooks, and the public syllabi of its courses).

| Variable | Values | Rule |
|---|---|---|
| `univ_stance`, `dept_stance` | encourage · permit with conditions · restrict · instructor decides · none found | "Encourage" needs active promotion (AI use built into teaching). "Restrict" means banned by default. "Instructor decides" means the official text leaves it to each course. |
| `univ_tone`, `dept_tone` | positive · neutral · cautionary · none found | Judged from the statement as a whole, with one quote that shows it. |
| `collaboration` | explicit · in passing · not discussed | Does official text describe working **with** AI (as partner, tutor, pair programmer) rather than only rules about its use? |
| `disclosure` | required · encouraged · not stated | Must students say when they used AI? |
| `se_courses` | AI built into the course · allowed with conditions · prohibited · not addressed · no public syllabus found | From public pages of the department's software engineering course(s) only. |
| `source_type` (per value) | policy page · guidance page · handbook · syllabus · news or announcement | |

Every coded value carries: the value, a quote of at most 40 words copied from the archived page,
the page URL, the archive file path, and the retrieval time. No value without a quote, except
"none found" values, which point to the search log instead.

**Fixed search, the same for every school** (so "none found" means the same thing everywhere):
1. The university's main AI guidance page (provost, teaching center, or integrity office).
2. The CS department site: home, undergraduate pages, handbook, academic integrity page.
3. Four web searches, recorded with their results in the school's search log:
   `<domain> generative AI policy`, `<domain> computer science AI policy`,
   `<domain> software engineering syllabus AI`, `<domain> ChatGPT academic integrity`.
4. Stop after 25 minutes or when every variable has a source, whichever comes first.

## Tasks
1. `data/frame/SOURCES.md`: URLs, download time, SHA-256 of each zip, field names used.
2. `study/codebook.md`: the codebook above, versioned. Any change after the pilot becomes
   version 2, with the reason, and pilot schools are re-coded under it.
3. Archive: every page behind a coded value saved with `curl` as
   `data/sources/<school>/<date>-<name>.html` (real bytes). If a page builds its text with
   JavaScript, so the quote is not in the curl copy, also save the rendered text from Claude's
   browser as `<same name>.rendered.txt` and say so in the row. PDFs saved as `.pdf`.
   Each school gets `data/sources/<school>/search-log.md` (queries, results, what was opened).
4. **Pilot, 5 schools, one per stratum** (the first drawn in each: Minnesota, Johns Hopkins,
   Valparaiso, Coppin State, Snow). Measure time and plan-limit points per school. Revise the
   codebook if it fails on real pages. Report pace against the deadline before continuing.
5. Code the other 10. Output: `data/coded/schools.csv` (one row per school) and
   `data/coded/values.json` (every value with quote, URL, archive path, time).
6. `study/check_sources.py` plus tests: every quote must appear in its archived file (spacing
   and case ignored); every archive file must exist; every school must have a search log; every
   variable must be filled. Recorded runs in `validation/runs/`, with one deliberate mutation run
   (a quote altered, the check must fail).
7. **Blind check by Marcus on 3 schools** (drawn at random from the 15 with a recorded seed).
   He codes them from the archived pages using a worksheet, without seeing Claude's values.
   Then: agreement per variable, and every disagreement listed with how it was resolved. With 3
   schools a kappa statistic would be meaningless, so percent agreement and the disagreement list
   are reported instead.

## Acceptance checks (Claude runs and records)
- [ ] `check_sources.py` passes on all 15 schools; the mutation run fails; both recorded.
- [ ] Every "none found" has a search log with all four searches.
- [ ] Agreement with Marcus computed and saved in `data/coded/agreement.json`.
- [ ] Web and pipeline tests still pass, recorded.

## Marcus's checklist (end of Phase 2; no code reading needed)
- [ ] On GitHub, open `data/frame/sample.csv`: 15 rows, Ohio State and Cincinnati marked
      "fixed by Marcus".
- [ ] Pick any school folder in `data/sources/`. Open its `search-log.md` and one saved page. Find
      in that page the quote that `data/coded/values.json` gives for it (Ctrl+F).
- [ ] Fill in the blind worksheet for your 3 schools before looking at Claude's codes.
- [ ] Read the agreement result. Does each disagreement's resolution seem fair to you?

## Changes this spec makes to the project spec (applied once approved)
- Hand-coded schools: **3, not 10.** The project spec says 10, written when the sample was 40;
  10 of 15 would make Marcus code two thirds of the study by the deadline.

## Budget
At the start of this phase (10:00 Nov 11): 5-hour 10%, weekly 9%. The pilot measures cost per
school; Claude reports the projection after the pilot. A `/compact` is prepared after the pilot
and again at the end of the phase.

## Questions for Marcus
1. Approve the design and the drawn list as they stand? (Changing the design means re-running the
   draw with the same seed and saying so.)
2. Blind check on 3 schools: acceptable, or another number?
3. Cheaper model for the bulk work? Claude's recommendation: no. Coding quality is the point of the
   study and the weekly limit is at 9%; revisit only if the pilot shows the 5-hour limit blocking
   the deadline.

## Out of scope
- Pages behind logins (LMS, private syllabi). Their absence is noted, not worked around.
- Interviews or emails to departments.
- Statistical tests. Groups of 2 do not support them.
