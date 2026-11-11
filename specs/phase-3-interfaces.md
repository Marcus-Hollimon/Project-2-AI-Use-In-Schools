# Phase 3: Interfaces (the four tabs with real data)

Goal: replace the four "Not built yet" pages on the site with pages built from the files the
project already records, so a reader can check every number and quote without opening the
repository.

Status: DONE 2026-11-11T12:22:58-05:00 (acceptance checks and Marcus's checklist ticked). Written by Claude 2026-11-11 at Phase 3 start. Marcus decided in advance (2026-11-11):
no hand-coding, tests prove quality, finish properly. Phase 4 then reviews the evidence: every
claim on the site traces to a test or a source.

## Rules for every tab
- **Static and built from repository files.** The pages read the JSON files below at build time;
  nothing is typed into the page by hand. When a file changes and the site is rebuilt, the page
  changes with it. No server, no database (project spec, "Out of scope").
- **Nothing private.** Only files already in the repository are shown. Raw transcripts are never
  read by the site.
- **Times in Eastern time**, as the progress files record them.
- **Tests** live in `web/src/*.test.jsx`, run with `npm run test:record` in `web/`, and are recorded
  in `validation/runs/`. Each tab's tests load the real data files, not made-up copies, so a test
  fails if the page and the data disagree.

## Found at Phase 3 start (fixed before building the tabs)
Seven usage readings written since 11:08 had 5 columns instead of 7 and sat below the "Cost per
phase" table in `progress/usage.md`. The pipeline read them with every value one column off
("66" as the moment, "195,190" as the weekly %), invented phases named after moments, and left
those readings out of check C1. Nothing failed. Fix: the rows were moved into the table with the
Phase and reset columns filled (values unchanged), and `build.py` now stops with an error on a
row that has the wrong number of cells, an unknown phase, or a non-number in a % column
(pipeline test `test_usage_row_with_missing_columns_stops_the_build`). C1 now checks 27 readings
instead of 20.

Found while building tab 1: a text fragment of the form "first four words,last four words"
highlighted the wrong passage on MIT's 6.102 page. An earlier sentence also starts "You may not
use", so the browser highlighted everything from there down to the quote's last words. Fix: the
link carries the whole quote (all 42 quotes have no "..." and are at most 182 characters), so it
either lands on the exact sentence or opens the page at the top. Checked in the browser pane at
Phase 3: the MIT link now highlights exactly the quote, across the `<em>` tags that broke Ctrl+F.
The pages also showed "FAIL" for checks that do not apply to a school (S1 to S5 and C3 for a
school with no quotes); they now show "n/a", and a test compares every cell with `checks.json`.

## Tab 1: Research findings
Reads `data/coded/values.json` (the coded values), `data/frame/sample.csv` (each school's group
and stratum), and `data/coded/checks.json` (whether each school passed the study checks).

Shows:
1. A label at the top: **descriptive only**. Two schools per stratum nationally, five in Ohio;
   the groups are too small for percentages or significance claims. Counts only, no percentages.
2. One table per question (stance, tone, collaboration, disclosure, software engineering
   courses): how many schools gave each answer, with columns for the five national strata and a
   separate Ohio column. **Ohio is never added into the national counts.**
3. A table of all 15 schools (name, group, stratum, the seven values), filterable by group.
   Opening a school shows, for each value: the quote, the source type, the coder's note, and two
   links:
   - **"Open the live page at this quote"**: the source URL with a text fragment holding the
     whole quote (`#:~:text=the quote`), which current Chrome, Edge, Firefox (131+) and Safari
     (16.1+) use to scroll to the quote and highlight it; other browsers open the page at the top
     (caniuse.com/url-scroll-to-text-fragment, web.dev/articles/text-fragments). This answers
     Marcus's Phase 2 report that Ctrl+F on the saved HTML could not find an MIT quote (the saved
     file had `<em>` tags inside it).
   - **"Saved copy"**: the archived file in the repository, for when the live page has changed.
   For a "none found" style value, it shows the pages reviewed and links to the school's search log.
4. The R1 re-fetch result in one line (pages checked, coded quotes still present), linking to
   `data/coded/refetch-report.md`.

Tests: the counts in every table add up to 10 national and 5 Ohio schools for every question
(2 in each stratum);
each count equals a count taken directly from `values.json`; every quote shown has a live link
containing `#:~:text=` and a saved-copy link to a file that exists; every absence value links to
a search log; the descriptive label is on the page.

## Tab 2: Validation
Reads every file in `validation/runs/` (each recorded test run), `data/coded/checks.json` (the
study checks per school) and `data/coded/refetch-report.json`.

Shows:
1. Totals: runs recorded, tests run, runs with a failure.
2. Every run in a list, newest first: time, suite (web, pipeline, study), phase, label, passed
   and failed counts, the commit it ran on. Filters: **phase**, **suite**, **status** (all,
   passed, had failures) and a **search box** that matches run labels and test names. Opening a
   run lists each test with its result and, for failures, the failure message.
3. **Errors caught**: the runs that had failures, each with what failed, so a reader sees what
   the checks stopped (for example the mutation run that disabled check S2).
4. **Study checks**: a table of the 15 schools and checks S1 to S5, C1 to C4, pass or fail, with
   what each check means in one line.

Tests: the page lists exactly as many runs as there are files in `validation/runs/`; the status
filter "had failures" shows only runs with failed tests, and they are listed under "Errors
caught"; the phase and suite filters show only matching runs; searching a test name finds the run
that contains it; the study table has 15 schools.

## Tab 3: Contributions
Reads `data/derived/contributions.json` (built by `pipeline/build.py` from this project's
transcripts, `progress/log.md`, `progress/decisions.md` and git history).

Shows a timeline, oldest first, grouped by day. Each entry: time, **who** (Marcus or Claude, as a
coloured badge), kind (prompt, reply, decision, milestone, commit, command), phase, and text.
Filters by who, kind and phase, plus a search box. Each of Marcus's prompts shows in full, with
Claude's reply to that prompt directly under it (collapsed until opened). Counts at the top: how
many entries each person has, by kind.

Pipeline change: prompt, reply and command entries get a phase the same way token responses do
(the latest usage reading at or before them).

Tests: the number of entries shown with no filters equals the file; every prompt has its reply
reachable from it; filtering by Marcus shows no Claude entries and the reverse; every entry has a
phase.

## Tab 4: Token usage
Reads `data/derived/tokens.json` (built by `pipeline/build.py`) and `data/derived/checks.json`.

Shows:
1. The four token classes as separate totals (input, cache write, cache read, output), with
   thinking shown as part of output, never added on top.
2. **Deduplication**: responses counted once (550 from 1,467 usage rows at Phase 3 start), and
   what summing rows would have shown instead.
3. Tokens by phase (the four classes, responses, average context).
4. **Plan-limit readings**: every reading in `progress/usage.md` (time, phase, moment, 5-hour %,
   weekly %, context tokens, reset before it).
5. **/clear compared with /compact**: one table with every context reset (when, which kind, context
   tokens before and after, 5-hour % before and after), and a short reading of what it shows.
6. The pipeline's checks (C1 to C3, privacy) with pass or fail.

Tests: the four totals equal the file's totals and equal the sum of the per-response rows; the
by-phase rows add up to the totals; there is at least one /clear and one /compact row; every
reading in the file is in the readings table.

## Acceptance checks (Claude)
- [x] Each tab shows real data, and its tests (above) pass in a recorded web run
  (`validation/runs/2026-11-11T17-10-16-827Z_web.json`, 37/37; mutation run
  `2026-11-11T17-07-38-873Z_web.json`: Ohio added into national counts, 2 tests failed).
- [x] Pipeline tests pass in a recorded run after the build.py changes
  (`2026-11-11T17-07-57-189Z_pipeline.json`, 13/13).
- [x] The live site (GitHub Pages) shows all four tabs after the push, checked in the browser pane
  (2026-11-11 12:13, footer commit 862b16f: 7 tables on Research, 28 runs on Validation, 118
  entries on Contributions, 4 tables on Token usage).
- [x] One text-fragment link opened in the browser pane lands on and highlights its quote (MIT
  6.102, 2026-11-11, after the whole-quote fix above).

## Marcus's checklist (no code needed)
Open the live site: https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
1. [x] **Research findings.** The page says the findings are descriptive. In any table, the
   numbers in each national column add up to 2 and the Ohio column adds up to 5. Open MIT and
   click "Open the live page at this quote" for the software engineering course: the page opens
   with the sentence highlighted (or, in an older browser, use Ctrl+F on a few words).
   (Marcus, screenshots, 2026-11-11: MIT software engineering link opened with the sentence highlighted.)
2. [x] **Validation.** Set the status filter to "had failures": every run shown has a failed
   count above 0. Type `test_s2` in the search box: runs from the study suite appear.
   (Marcus, screenshots, 2026-11-11: "had failures" plus search `test_s2` showed 1 run, the S2 mutation, 1 failed.)
3. [x] **Contributions.** Filter to Marcus: only your prompts, decisions and commands remain. Open
   one of your prompts: Claude's reply is under it.
   (Marcus, screenshots, 2026-11-11: one of his prompts opened with Claude's reply under it.)
4. [x] **Token usage.** Four separate token totals are shown. The reset table has a /clear row
   (Nov 11, about 10:00) and several /compact rows.
   (Marcus, screenshots, 2026-11-11: "Token tables are there".)
