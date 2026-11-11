# State: read this first

Current phase: 3 Interfaces is DONE (Marcus's checklist ticked). Next: Phase 4 Validation, spec first.

Last updated: 2026-11-11T12:22:58-05:00 by Claude (session a9056776), just before the eighth `/compact` (Phase 3 end).

## Phase 3 done: Marcus's checklist ticked 2026-11-11T12:22:58-05:00 from his screenshots

## Phase 3 tabs built (11:58 to 2026-11-11T12:11:20-05:00 Nov 11; 5-hour 74% to 85%)
- Spec: `specs/phase-3-interfaces.md`. All four tabs read repository files at build time through
  `web/src/data.js`; pages in `web/src/tabs/`; tests in `web/src/tabs.test.jsx` (20 tests, real data).
- Pushed as 862b16f. Recorded: web 37/37 (`validation/runs/2026-11-11T17-10-16-827Z_web.json`),
  pipeline 13/13 (`2026-11-11T17-07-57-189Z_pipeline.json`), mutation "Ohio added into national
  counts" failed 2 tests (`2026-11-11T17-07-38-873Z_web.json`).
- Fixed on the way (each written up in the spec): 7 malformed `usage.md` rows (build.py now rejects
  them); text-fragment links now carry the whole quote (first,last words highlighted the wrong MIT
  passage; checked in the browser pane); study cells that do not apply show n/a, not FAIL; three
  runs recorded while STATE.md still said Phase 2 had their phase corrected to 3 with a
  `correction` field saying so.
- Dev server: `C:\Claude Folder\.claude\launch.json` entry `project2-web` (outside the repo; the
  preview tool reads only that folder), then open `http://localhost:5173/Project-2-AI-Use-In-Schools/`.

## Phase 2 done (wrap-up 11:28 to 2026-11-11T11:33:07-05:00 Nov 11; 5-hour 69% to 71%)
- R1 re-fetch: `study/refetch.py` fetches every archived URL again with save_page.py's exact curl
  command into a temp folder, compares SHA-256, and for changed pages looks for every coded quote in
  the new copy. Report: `data/coded/refetch-report.md` and `.json`. Final run: 69 pages, 41
  unchanged, 26 changed (HTML that changes bytes per load), 2 refused (HTTP 403, no coded quotes),
  **0 coded quotes missing**. Some sites (Johns Hopkins teaching pages) answer 403 on one run and 200
  on the next; a 403 is reported as "refused", not "gone". Follow-up notes, including a browser-pane
  check of the Johns Hopkins guidelines page, live in `data/coded/refetch-notes.md` and are copied
  into the report on every run.
- Recorded at Phase 2 end: web 17/17 (`validation/runs/2026-11-11T16-32-19-757Z_web.json`), pipeline
  12/12 (`2026-11-11T16-32-23-272Z_pipeline.json`), study 33/33 (`2026-11-11T16-32-24-131Z_study.json`);
  the mutation run (S2 disabled, 1 failed) is `2026-11-11T15-20-17-071Z_study.json`. check_study: all
  15 PASS. All four acceptance boxes in `specs/phase-2-study.md` are ticked.
- Marcus's 3-step checklist (in the spec) was handed to him at Phase 2 end; not yet confirmed done.

## Main coding done (11:16 to 11:24 Nov 11; 5-hour 59% to 66%)
- `check_study.py` with no `--only`: all 15 PASS, "All checks pass: True" (11:24:02). Study tests
  33/33 recorded (`validation/runs/2026-11-11T16-24-02-902Z_study.json`).
- Ohio State 204796: university **restrict** (ai.osu.edu Responsible Use: GenAI for coursework only
  with each instructor's explicit permission; cue_reason), tone positive (AI Fluency FAQ). CSE site
  cse.osu.edu gives curl 403; read in the browser pane (no AI rule), dept "none found" from the search
  log. The official CSE 3231 syllabus site (syllabi.engineering.osu.edu) is curl 403 and the browser
  pane is refused: se_courses "no public syllabus found".
- Baldwin Wallace 201195: all absences (handbook revised Aug 2026 and the 2026-27 catalog honesty
  policy say nothing on AI; catalog.bw.edu gives curl HTTP 202 empty, read in the browser pane).
- Defiance 202514: the only rule is the library's AI guide: restrict ("Unauthorized use ... is
  considered cheating"), cautionary, disclosure **required** ("necessary to cite"; cue_reason).
- Columbus State 202222: Standard Syllabus Statement: restrict ("may not use ... unless explicitly
  permitted"), neutral, disclosure required. se_courses **prohibited**: the CSCI 2221 Spring 2026
  syllabus (Word file) has no course rule and adopts the college statement by reference (cue_reason).
  This is the one judgment call worth Marcus's eye.
- A time typed from memory slipped into the Baldwin Wallace cost row and was replaced with a
  `date -Iseconds` reading (marked "written late").

## Main coding, earlier batches
- Le Moyne-Owen 220604, Luzerne 213659, Cincinnati 201885 coded and passing (11:09 to 11:14; 5-hour
  52% to 57%). Le Moyne-Owen: all absences (handbook and catalog say nothing on AI). Luzerne: the AI
  rule is in the Academic Honesty Policy, a **Word file**; `save_page.py` now saves Word files as
  `.docx`, `study/docx_text.py <archive>` writes the `.docx.txt` the checker reads (like a PDF's
  sidecar), new test, study 33/33 (`validation/runs/2026-11-11T16-12-28-115Z_study.json`).
  Cincinnati: the software engineering course site (uc3093c.github.io) is 404, so se_courses is
  "no public syllabus found".
- Small colleges again returned no own-domain pages from the fixed searches; run the two extra
  `allowed_domains` searches (policy/handbook, CS program/catalog) right after the fixed six.
- Virginia 234076, MIT 166683, Presbyterian 218539 coded and passing (11:00 to 11:06; 5-hour 45% to
  49%, about 1.3 points per school). Rows in `progress/pilot-cost.md`, "Main coding".
- Virginia: the CS department site (engineering.virginia.edu) gives curl HTTP 403 and the browser
  pane could not open it ("navigation denied or failed"); department coded "none found" from the
  search log, with a note saying so. Do not retry it with browser headers.
- Presbyterian: the fixed searches returned no presby.edu pages at all; extra searches with
  `allowed_domains: ["presby.edu"]` found the Blue Book and catalog. Use `allowed_domains` early for
  small colleges.
- Lessons: `unitid` in values.json is a **string** (an int made the checker say "not coded yet");
  for a PDF the value's `archive` is the `.pdf`, not the `.pdf.txt`; the checker joins HTML text
  pieces with a space, so a quote ending right after `</strong>` or `</em>` fails S1 on the period
  (drop the trailing period).

## Deadline and pace
- Everything is due **2 PM EST, Thu Nov 12 2026** (Marcus, 2026-11-11).
- Weekly limit 10% (resets Tue Nov 17 01:00 EST). **The 5-hour window is the real constraint**:
  it went 10% to 22% from 10:00 to 10:21 Nov 11 while context grew 78k to 198k. It resets 14:40 EST.
- Marcus wants a `/compact` prepared at every phase end and after each big chunk (CLAUDE.md).
- Marcus asked (10:15 Nov 11): **no Coaching sections** any more, despite the global CLAUDE.md
  rule and the per-turn hook; and no plan mode. "Let's just try and get this done properly."

## FIRST, right after the /compact
1. Take a usage reading marked "after /compact (phase start)" in `progress/usage.md` (tool:
   get_usage), as a full 7-column row inserted in the main table (Phase 4), with the time from
   `date -Iseconds`. Never append at the end of the file: that lands below "Cost per phase".
   Then update the header line here to "Current phase: 4" BEFORE recording any test run (the
   recorders read the phase from it). Run `uv run --project pipeline python pipeline/build.py`.
2. Phase 4 Validation (`specs/00-project.md`: "Validation tab complete, evidence review"; exit check:
   "Any claim on the site traces to a test or a source"). Write `specs/phase-4-validation.md`
   FIRST. Idea: a list of every claim the site makes (each number and sentence that states a fact),
   each linked to the test or file that backs it, shown on the Validation tab and checked by a test
   that fails when a claim has no backing. Also consider real errors caught outside test runs (the
   usage.md rows, the CIP frame, the guessed times, the text-fragment highlight), today only in
   log.md and the specs.
3. Budget: 5-hour was 87% at 12:23 and resets 14:40 EST. Phase 3's build cost about 11 points.
   Write the Phase 4 spec before the reset if it fits; build after.

## Pilot result (details and costs in `progress/pilot-cost.md`)
- Minnesota 174066, Johns Hopkins 162928, Valparaiso 152600, Coppin State 162283, Snow 230597:
  coded and all pass `check_study.py`. Average 2.6 five-hour points and about 35,800 tokens of
  context per school, falling as the procedure settled. Projection: the 10 left take about 35
  points with compacts; 5-hour was 40% at 10:52 and resets 14:40 EST.
- **Codebook v2 adopted** (all four pilot candidates; reasons in `study/codebook.md`, "Changes in
  version 2"): pre-2023 course pages count as "no public syllabus found"; example syllabus language
  telling students to disclose is "encouraged"; news on the department site is department text;
  a rule against only "inappropriate or excessive" use is "permit with conditions" ("unauthorized"
  use is "restrict"). Recoded the pilot (spec R2): one value changed (Johns Hopkins `se_courses`),
  saved in `data/coded/codebook-v2-recode.json`. `values.json` and `codebook.json` say version 2.
- Check S3 changed during the pilot: browser text (`--rendered`) passes with a raw curl copy at
  HTTP 200, or at HTTP 403 plus a written `fetch_reason` on the value (spec and test updated; sabotage
  run failed exactly the new test). Not yet needed by any coded value.
- `.gitattributes` stores `data/sources/**` byte-for-byte (`-text`); without it git rewrote line
  endings in archives, which would break S2 hashes on a fresh checkout.
- Helpers: a scratch text viewer (`showtext.py` in the session scratchpad
  `C:/Users/junni/AppData/Local/Temp/claude/3662653f92cacdd2/a9056776-4951-4636-a9ad-acb1dbccb955/scratchpad/`:
  `python -I showtext.py <file> [regex] [maxchars]` prints a saved page's visible text filtered by
  a regex) and `pdftotext -enc UTF-8 <pdf> <pdf>.txt` for the PDF sidecar. For PDFs, `grep -o -iE
  ".{0,120}(pattern).{0,120}"` on the .txt; never print whole sections (one 45-line print cost 8k tokens).
- `save_page.py` adds the file extension itself: name a PDF `student-handbook`, not `student-handbook.pdf`.
- Do NOT retry curl with extra browser headers when a site returns 403: the permission system refused
  it as bot-check circumvention. Read such pages in the browser pane instead.
- ddc7d76a: checked with Marcus's permission (metadata only); it is the retired canon-keeper project
  (Sep 9), not this one. Closed.
- Prompts: Marcus reaffirmed at 10:47 that all his prompts are published in full (public repo,
  `data/derived/contributions.json`); he may ask to hide some later. Hiding later does not remove
  them from git history.

## Where things stand
- Phases 0 and 1: done. Live site still a skeleton:
  https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Phase 2 spec `specs/phase-2-study.md`: approved 10:15 Nov 11. **No hand-coding by Marcus**;
  quality is shown by the 10 automated checks in the spec (S1 to S5, C1 to C4, N1, plus R1 and R2).
- Done in Phase 2: IPEDS 2024 frame (`data/frame/`, 1,509 schools, 5 strata, 2025 Carnegie), 15
  schools drawn (`data/frame/sample.csv`, seed 20261111). The pre-clear plan (CIP 11.07 only)
  would have excluded Ohio State and Cincinnati; fixed with 11.0701 or 11.0101.
- Codebook v1 frozen: `study/codebook.json` (allowed values, cue words, required searches) and
  `study/codebook.md` (rules). Variables: univ_stance, univ_tone, dept_stance, dept_tone,
  collaboration, disclosure, se_courses.
- Tools: `study/save_page.py` (curl archive plus `.meta.json` with status, final URL, SHA-256;
  `--rendered` for JavaScript pages, needs a raw curl copy of the same URL too),
  `study/check_study.py` (writes `data/coded/checks.json`). Commands in the project CLAUDE.md.
- Tests: study 32/32 (latest `validation/runs/2026-11-11T15-53-30-496Z_study.json`); earlier study 31/31 (mutation run with S2 disabled failed exactly the S2 test; restored), pipeline
  12/12, web 17/17; all recorded. CI runs all three suites before deploy (pushed 5ccc209).

## How to code one school (spec task 4; same for the pilot and the 10 left)
For each school, slug `<unitid>-<short name>` (e.g. `174066-minnesota`):
1. Run the 4 required searches from `codebook.json` with WebSearch, `{domain}` = the domain above.
   Write `data/sources/<slug>/search-log.md`: one `## Search: <exact query>` heading per search, then
   one `- <url> (what it was; opened or not; saved as ...)` line per relevant result, or
   `- no relevant results`. The checker needs every heading and at least one line under each.
2. Find the university AI guidance page and the CS department pages (spec "Fixed search").
3. Save each page behind a value with `save_page.py`. Open the saved file's text to copy quotes
   exactly (quotes at most 40 words). If curl gets a 403 or an empty JavaScript shell, save the
   browser pane's text with `--rendered` (the raw curl copy must also exist with HTTP 200).
4. Add the school to `data/coded/values.json`:
   `{"codebook_version": 2, "schools": [{"unitid", "slug", "name", "values": {var: entry}}]}`.
   Entry with evidence: value, quote, url, archive (repo-relative path), source_type, optional
   cue_reason, optional domain_reason. Absence entry: value plus `reviewed` (list of archive paths)
   or `search_log` (path). For every "none found" or "no public syllabus found", also run and log
   the 2 `second_searches`.
5. Run `check_study.py --only <unitid>`; fix until it passes. Note time and a get_usage reading per
   school in `progress/pilot-cost.md` (time taken, 5-hour points, context growth).
Codebook is frozen at version 2 for the 10 remaining schools. A further change would be version 3,
with reasons in `codebook.md`, and every coded school recoded (spec R2); avoid it unless a rule is wrong.

## Still open
- Nothing waiting on Marcus.

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38 Nov 8, then claude-opus-5-5 | planning, audit, Phase 0, first /compact (Nov 8 00:57), Phase 1, ends with the /clear |
| a9056776-4951-4636-a9ad-acb1dbccb955 | `C:\Claude Folder` (same folder) | claude-opus-5-5 | starts after the /clear (Nov 11 10:00:07); Phase 2 |

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. Write prose and Markdown with the file-writing tool; keep backslash escapes out of code
  (build them with `chr(92)` in Python if needed).
- The session's working directory is `C:\Claude Folder`, one level above the repo; use absolute paths.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
- The Claude app shows Marcus no context-token number. Never write a checklist step that needs one.
