# Phase 5: More schools (15 to 36)

Goal: give the Research findings tab enough schools to compare **types of school**, not just
describe single schools. Today each type has 2 schools nationally; this phase raises that to 6.

Status: **approved by Marcus at 2026-11-11T15:15:40-05:00** (transcript time) ("I approve. Lets do it, BUT add another ohio
school sure!"). His addition: one more Ohio school (below), so 21 new schools and 36 in all. This
amendment was pushed before the draw ran. Marcus asked for this phase at
2026-11-11T15:08:57-05:00 ("Before doing the evaluation and spec writing can we add some more
schools?") and chose 20 more schools, 6 per type, by replying "Yes, write the spec" at
2026-11-11T15:10:24-05:00 (both times from the session transcript). No school is drawn or coded
until he approves this spec. (Approved; see Status.)

## Why (what the first 15 schools show)
- 14 of 15 CS departments published nothing we could find about AI. The universities do the talking.
- University stances split: 5 restrict AI by default, 5 leave it to each instructor, 2 permit it
  with conditions, 3 published nothing we found.
- With 2 schools per type, none of this can be compared across types. With 6 per type, the counts
  start to show whether, for example, community colleges lean toward restricting AI more than
  research universities do. Still descriptive: 6 is too few for statistical tests.

Hard truth: more schools will probably not change the department finding much (more silent
departments mostly confirm it). The gain is in comparing universities by type.

## Phase numbers change
This work becomes **Phase 5**. Marcus's evaluation, reflection and presentation move to
**Phase 6**. The usage reading already recorded at 15:06:20 as "Phase 5 start" stays correct. Code
change: add `"6"` to the phase lists in `pipeline/build.py` (`PHASES`), `web/src/data.js`
(`PHASE_ORDER`) and `web/src/tabs/Contributions.jsx` (`PHASES`). `specs/00-project.md` gets the
new phase row and deliverable 1's "Done when" says 36 schools.

## The draw (round 2)
- **Who:** 4 more schools in each of the 5 national strata (S1 to S5), drawn at random from the same
  frame (`data/frame/frame.csv`, 1,461 national schools), leaving out Ohio and the 10 national
  schools already drawn.
- **Plus 1 Ohio school** (Marcus, at approval): drawn at random from Ohio's S2 (private R1), the only
  type with no Ohio school in the sample. The frame has two: Case Western Reserve University
  (201645) and University of Dayton (202480). Drawn after the national round 2, from the same
  round-2 generator. Ohio then has 6 schools, one in every type and both fixed schools in S1.
- **Seed: 20261115**, named here before any run. This spec is pushed to GitHub before the draw runs,
  so GitHub's copy shows the seed was fixed first (round 1's seed was only committed locally first).
- **How:** `study/draw_sample.py` keeps round 1 exactly as it is (same seed, same code path), then
  draws round 2 with the new seed from a separate random generator. New rows are marked
  `how = "random, round 2"`. The first 15 rows of `sample.csv` must stay byte for byte the same.
- **No replacements.** If a drawn school has a dead website or publishes nothing, it stays in and is
  coded "none found" through the same fixed search. Swapping it out would make the sample chosen,
  not random.
- A second run must reproduce `sample.csv` byte for byte.

## Coding (unchanged from Phase 2)
- **Codebook v2, frozen.** No codebook changes in this phase. A hard case goes through check C3's
  written reason, which the site shows. If a real gap appears that a written reason cannot cover,
  Claude stops and asks Marcus before changing anything.
- The same fixed search for every school (`specs/phase-2-study.md`), plus the two extra
  `allowed_domains` searches for small colleges that Phase 2 found necessary.
- Every page behind a value is archived with `study/save_page.py`. Curl-blocked pages follow the
  Phase 2 rule (browser text plus the raw 403 copy and a written reason). Never retry curl with
  browser headers; never complete a CAPTCHA.
- **Change made while coding (2026-11-11, 16:22 EST, Westminster):** catalog.westminster.edu answers
  curl with HTTP 202 and an empty body (a bot challenge) instead of 403. Check S3 now treats a raw copy
  that is HTTP 202 **and** zero bytes as blocked, like 403, so it still needs a written `fetch_reason`;
  a 202 with any body still fails. New test `test_s3_rendered_text_with_empty_202_raw_copy_needs_fetch_reason`;
  study tests 39/39 (`validation/runs/2026-11-11T21-24-25-844Z_study.json`). This is a check change, not
  a codebook change; it is on Marcus's list of judgment calls, and reverting it would leave Westminster's
  university values without an archive the checker accepts.
- **Checker bug fixed while coding (2026-11-11, 16:26 EST, Niagara CC):** the checker took a school's
  domain as the last two parts of its IPEDS web address, so Niagara CC (www.niagaracc.suny.edu) became
  `suny.edu`, which would accept any SUNY campus's page under S4 and expected searches for "suny.edu ...".
  Maine Fort Kent (umfk.maine.edu, the University of Maine System) had the same fault. The checker now keeps
  the campus subdomain for six system domains shared by separate colleges (suny.edu, cuny.edu, kctcs.edu,
  maine.edu, mass.edu, losrios.edu); single universities with campus subdomains (umn.edu, psu.edu, iu.edu,
  mit.edu) keep the two-part domain. No school coded earlier is affected. New test
  `test_registrable_domain_keeps_campus_of_college_systems`; study tests 40/40
  (`validation/runs/2026-11-11T21-27-37-461Z_study.json`).
- **Order: round robin by type** (S1, S2, S3, S4, S5, then again; the Ohio school last), so if the budget runs out early,
  every type still has the same number of schools.
- A school counts as done only when `check_study.py` passes every check (S1 to S5, C1 to C4, N1)
  for it. Each school's time and plan-limit points go in `progress/pilot-cost.md` under a new
  "Phase 5" table.

## Budget and stop rules
- Measured in Phase 2: about 2 points of the 5-hour limit per school including compacts, and about
  0.3 points of the weekly limit. 21 schools: about 40 to 50 five-hour points, weekly 22% to about 30%.
- At 15:06 the 5-hour window was 10%; it resets at 19:40 EST.
- **Stop rules:** pause coding if the 5-hour window reaches 85% (wait for the reset); stop the
  phase and report to Marcus if the weekly limit reaches 40%, or if it is past 10:00 EST Nov 12
  with schools left. Schools already coded stay; the site reports however many were finished.
- A `/compact` is prepared about every 4 schools (Marcus types it), with readings just before and
  after, as in CLAUDE.md.

## Site changes
- The Research tab already counts schools from the data, so most of it updates by itself.
- Text that says "15" in test names, comments and docstrings is updated; the claims register
  (`validation/claims.json`) follows any renamed test.
- **New: a short "What the data shows" list** on the Research tab: 3 to 5 sentences, each computed
  from `values.json` and `sample.csv` (for example, how many departments published nothing, and the
  university stances by type). Counts only, no percentages (groups are small). Each sentence is
  registered in `validation/claims.json` and backed by a test that recomputes it from the files.

## Tests
- New study test: round 1 rows are unchanged, round 2 has 4 per national stratum and 1 Ohio S2
  school, no school appears twice, and the draw is reproducible.
- One recorded mutation run that must fail (for example, round 2 allowed to redraw a round 1 school),
  followed by a passing run (pipeline check C6).
- Web tests for the new findings sentences, including a mutation run (a wrong count must fail).

## Acceptance checks (Claude runs and records)
- [ ] This spec pushed to GitHub before the draw ran (commit time on GitHub earlier than the draw).
- [ ] `sample.csv`: 36 rows; first 15 unchanged; second run identical.
- [ ] `check_study.py` passes every check on all 36 schools; results in `data/coded/checks.json`.
- [ ] R1 re-fetch report rerun over every archived page.
- [ ] Study, web and pipeline tests pass, recorded; each mutation run fails, recorded.
- [ ] `build.py` exits 0 with all checks passing; the live site deploys.

## Marcus's checklist (no code reading needed)
- [ ] On GitHub, open `data/frame/sample.csv`: 36 rows; the last 21 say "random, round 2" (20 national,
      1 Ohio); Ohio State and Cincinnati still say "fixed by Marcus".
- [ ] On the live site's Research findings tab, the table header says "National (of 30)" and "Ohio (of 6)", and
      the note says 6 in each of 5 strata.
- [ ] Pick one new school in the Research tab, open one of its source links, and Ctrl+F a few words
      of its quote on the page.
- [ ] On the Validation tab, the study check table lists 36 schools, all passing.

## Out of scope
- More than one extra Ohio school.
- Codebook changes, statistical tests, pages behind logins.
