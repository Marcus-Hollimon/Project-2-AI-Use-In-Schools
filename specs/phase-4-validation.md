# Phase 4: Validation (every claim on the site traces to a test or a source)

Goal (`specs/00-project.md`): "Validation tab complete, evidence review". Exit check: "Any claim on
the site traces to a test or a source."

Status: written by Claude 2026-11-11 at Phase 4 start, before any Phase 4 code. Marcus decided in
advance (2026-11-11): no hand-coding, tests prove quality, finish properly.

## The idea in one paragraph
Every sentence or number on the site that states a fact gets an entry in one list, the **claims
register** (`validation/claims.json`). Each entry says what backs the claim: a named test, a file
in the repository, or an outside source (a web page, with the date it was checked and what it
says). The Validation tab shows the whole list, so a reader can click from any claim to its
evidence. A test reads the rendered pages and **fails if any factual text on the site is not in the
register**, and fails if a register entry points at a test or file that does not exist. So the exit
check is enforced by a test, not by Claude's word.

## What counts as a claim
Two kinds of text appear on the site:
1. **Data**: numbers, quotes and rows drawn straight from a repository file (count tables, run
   list, timeline, token tables). The file is the source. These areas are marked in the page code
   with the file they come from (`data-from="data/coded/values.json"`), and the Phase 3 tests
   already compare them with the files.
2. **Prose**: sentences written into the page code (the "Descriptive only" note, "Nothing is left
   out", "thinking is counted inside output", the check descriptions). Each such element is marked
   `data-claim="<id>"` and has a register entry. Numbers computed inside prose (for example "6 of
   6 were deliberate mutations", "2.65 times") count as prose claims and need a test that
   recomputes them.

Text that states no fact (headings, filter labels) is not checked. As built, `data-claim="none"`
is allowed only on the small label above a page title (class `eyebrow`), and the test fails on any
other use. Counters such as "Showing 12 of 30 runs" sit inside a `data-from` area naming the file
they count, instead of being exempted.

## Found while surveying the site (fixed in this phase)
Read at Phase 4 start, from the page code in `web/src/`:
1. **"Nothing is left out" (Validation) is false as written.** GitHub runs every test suite before
   each deploy, and those runs are not recorded. Test commands Claude ran during development
   without the recorder (for example `pytest -q` straight from the shell) are not recorded either.
   Fix: the pipeline counts test commands in the transcripts that did not go through a recorder,
   and the page says plainly which runs the list holds and which it does not, with that count and a
   link to the GitHub Actions history. Pipeline test for the counter.
2. **"then removed (the next run passes)"** after each mutation is not checked by any test. Fix:
   a test that, for every mutation run, the next run of the same suite passed. If one did not,
   the sentence is reworded to what happened.
3. **The Research note says "5 in Ohio"** without saying two of them (Ohio State, Cincinnati) were
   chosen by Marcus, not drawn at random (`data/frame/sample.csv`, column `how`). The school rows
   say so; the note will too, with the count computed from the file.
4. **Statements about how Claude and Claude Code behave** have no cited source on the site:
   thinking tokens are counted inside output tokens; cache reads are cheap re-sends of the
   conversation; a /compact keeps a written summary; the overhead left after a reset is tool
   definitions, system prompt and skills. Fix: each gets an outside source in the register,
   read by Claude in the browser pane at Phase 4 (the page itself, not a search summary), with
   the date and a one-line paraphrase. A statement the source does not support is reworded or
   removed.
5. **"Read ... at every phase boundary and around every reset" (Token usage)** is untested. Fix:
   a test that every /clear and /compact has a reading before and after it, and that every phase
   has a starting reading. If an early phase has none, the sentence says which.
6. **The Overview sentence "Claude Code wrote the code, and Marcus supervised"** is backed today
   only by Marcus's decision. Fix: register entry citing `progress/decisions.md` and the
   Contributions timeline (Marcus's entries are prompts, decisions and commands; no commit
   entries carry his code). No new test: it is a statement of how the project was run, and the
   timeline is the evidence.

### Found during the build (also fixed)
7. **The Token usage summary promised a "new session" comparison** the page does not have. It now
   names only /clear and /compact.
8. **Finding 2's own wording was false.** On Nov 8 the first web mutation was followed by a second
   mutation, not a passing run. The sentence now says each mutation is followed by a passing run
   of the same suite once the bug is removed.
9. **Claude's first design for the mutation follow-up test could never pass**: a web test cannot
   see the run it is part of, so the newest mutation always looked unanswered. The clean run
   failed (`validation/runs/2026-11-11T17-42-46-143Z_web.json`, kept with a correction note). The
   check moved to the pipeline as **C6**, for the same reason C5 lives there.
10. **C3 failed on Marcus's /compact at 12:45**, which came right after a tool call he stopped. The
    rejection and the interrupt note were in the context but never answered, so the transcript's
    count was 508 tokens above the last response. C3 now allows a larger count only when such
    unanswered records exist, and lists them; every other /compact must still match exactly.
11. **"Before and after every reset" was no longer true**: no reading was taken just before the
    12:45 /compact (the 5-hour window had run out), and the reading after it was taken late. The
    Token usage page now names every reset with no reading just before it, computed from
    `progress/usage.md`, and its reset table marks the row.
12. **Claude reverted a page with `git checkout` while it held uncommitted work**, wiping the claim
    marks on the Token usage page. Caught by checking the diff, restored from a backup copy made
    beforehand; mutations after that were undone by copying a saved file back. Not a site error,
    so it is not in `caught.json`.

## Design
### 1. The claims register: `validation/claims.json`
One entry per claim:
- `id` (short, for example `research-descriptive`), `tab`, `claim` (the sentence in a few words);
- `kind`: `computed` (a number worked out by the page), `method` (how the project or study was
  done), or `external` (behaviour of software or a service not in this repository);
- backing, at least one of: `tests` (test names, each with its suite), `files` (repository paths),
  `sources` (each with `url`, `checked` date from `date -Iseconds`, and `says`, a one-line
  paraphrase, never a long quote).

### 2. Marking the pages
Every factual prose element on the five pages carries `data-claim`; every data area carries
`data-from`. The register, not the page, holds the evidence, so the page code stays short.

### 3. Tests (new web file `web/src/claims.test.jsx`)
1. Every element marked `data-claim` on the rendered pages has a register entry, and every
   register entry is found on its tab.
2. **No unmarked fact**: on every page, every paragraph, list item, definition and note inside the
   main area is marked `data-claim` or sits inside a `data-from` area. Adding a sentence without a
   register entry fails this test.
3. Every `files` path exists. Every `tests` name is defined in that suite's test source
   (`web/src/*.test.jsx`, `pipeline/tests/`, `study/tests/`). Every `sources` entry has a url,
   a checked date and a paraphrase.
4. The new numeric checks from the findings above (a reading around every reset, with exceptions
   named; the Ohio count; the re-check line; the unrecorded test-command count). The mutation
   follow-up became pipeline check C6 (finding 9).

### 4b. Pipeline check C6 (added during the build)
Every run labelled as a mutation (label starts with "mutation") has at least one failed test, and
a later run of the same suite that is not a mutation passed. Pipeline test for C6.

### 4. Pipeline check C5 (run by `build.py`, after test runs are recorded)
Every test named in the register **passed in the newest recorded run of its suite**. This runs in
the pipeline, not in the web tests, because a web test cannot see its own run's result. The
result is written to `data/derived/checks.json` and shown on the Validation tab beside each claim.
Pipeline test for C5, including a case where a backing test failed.

### 5. Validation tab additions
- **Claims and their evidence**: a table of every register entry (claim, tab, kind, evidence as
  links: test name with its newest recorded result, file, or outside page with the date checked).
  Filter by tab and kind.
- **Errors caught outside test runs**: problems found by reading, by the browser pane, by Marcus,
  or by a pipeline check rather than by a recorded test run. Held in `validation/caught.json`;
  each entry has when, who found it, what was wrong, how it was found, the fix, the test or check
  that now guards it (if any), and a link to the evidence (`progress/log.md` row, spec section,
  commit). Known at spec time, details to be taken from those files, not from memory: the three
  lines damaged by the shell tool (Phase 0, caught by lint); the unanswered retry that failed C2
  (Phase 1); the wrong time Claude typed that failed C1 (Phase 1); the CIP frame that would have
  dropped Ohio State and Cincinnati (Phase 2); the Ctrl+F miss Marcus reported on the MIT quote
  (Phase 2); the seven malformed usage rows, the text fragment that highlighted the wrong MIT
  passage, FAIL shown for checks that did not apply, and runs recorded under the wrong phase
  (Phase 3); and the findings in the section above (Phase 4). A test checks every entry has all
  fields and that each evidence link points at a file that exists.
- The run list's opening sentence is rewritten per finding 1.

### 6. Evidence review
After the build, Claude goes through the register once, claim by claim, and records the verdict
for each (backed as is, reworded, or removed) in a "Review results" section of this spec, with the
recorded run that proves the tests pass.

## Acceptance checks (Claude)
- [x] `claims.test.jsx` passes in a recorded web run, and the whole web suite passes: 48 of 48,
  `validation/runs/2026-11-11T19-49-22-555Z_web.json`.
- [x] Mutation: a sentence added to a page without a register entry makes the claims test fail
  (`2026-11-11T17-42-18-324Z_web.json`: 1 failed, the coverage test), then removed.
- [x] Mutation: a register entry pointing at a test name that does not exist fails
  (`2026-11-11T17-42-41-129Z_web.json`: 2 failed), then removed.
- [x] Pipeline tests pass in a recorded run, including C5, C6, the C3 stopped-turn rule and the
  unrecorded-run counter: 17 of 17, `2026-11-11T19-47-59-829Z_pipeline.json`. build.py reports
  C1, C2, C3, C5, C6 and privacy all PASS (30 test commands recorded, 17 not recorded).
- [x] Each outside source was read and its paraphrase matches it. The two platform.claude.com
  pages and code.claude.com/docs/en/costs were opened in the browser pane. The caniuse page did
  not render its table there, so its public data file on GitHub was read instead (the register
  cites that file, not the caniuse page).
- [ ] Live site after the push: the Validation tab shows the claims table and the errors-caught-
  outside-tests list (browser pane).
- [ ] Review results written below.

## Marcus's checklist (no code needed)
Open the live site: https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
1. [ ] **Validation, Claims and their evidence.** Pick any three claims and click their evidence:
   each opens a test result, a repository file, or an outside page that says what the claim says.
2. [ ] **Validation, Errors caught outside test runs.** The list includes the MIT quote you could
   not find with Ctrl+F, credited to you.
3. [ ] **Validation, run list.** The opening sentence says which runs are not in the list.
4. [ ] **Research findings.** The "Descriptive only" note says two Ohio schools were chosen by you.

## Review results
Claude went through the register (`validation/claims.json`, 23 claims) on 2026-11-11 after the
build. C5 PASS at the last build: every test named below passed in the newest recorded run of its
suite (web `2026-11-11T19-49-22-555Z`, pipeline `2026-11-11T19-47-59-829Z`, study
`2026-11-11T16-32-24-131Z`).

| Claim | Verdict |
|---|---|
| overview-lede | Backed as is: roles in CLAUDE.md and decisions.md; no commit in the timeline carries Marcus's code. |
| overview-cards | Backed as is: four Phase 3 tests compare each page with its file. |
| overview-repo | Backed as is: the paths exist. |
| research-lede | Backed as is: the four questions are the codebook's. |
| research-descriptive | Reworded: now says 2 of the 5 Ohio schools were chosen by Marcus (finding 3), with a test. |
| research-strata | Backed as is: draw_sample.py and SOURCES.md. |
| research-links | Backed as is, with an outside source: caniuse data (Chrome 81, Edge 83, Firefox 131, Safari 16.1). |
| research-refetch | Backed as is: a new test recomputes all three numbers from refetch-report.json. |
| validation-lede | Backed as is. |
| validation-scope | Reworded: "Nothing is left out" removed; the page states what the list does not hold, with the pipeline's count (finding 1). |
| validation-mutations | Reworded (finding 8) and now checked by pipeline check C6 (finding 9). |
| validation-claims | New in Phase 4; backed by the claims tests and C5. |
| validation-caught-outside | New in Phase 4; a test checks every entry is complete and its evidence exists. |
| validation-study | Backed as is: one study test per check. |
| contributions-lede | Backed as is. |
| contributions-source | Backed as is: the hide list is empty, now tested. |
| tokens-lede | Reworded: the "new session" comparison removed (finding 7). |
| tokens-thinking-cache | Backed as is, with outside sources: thinking counted in output; cache reads at 0.1x the input price (0.05x on Opus 5.5 and Sonnet 5.5). Cache reads being the largest class is now tested. |
| tokens-dedup | Backed as is: pipeline tests and the session-1 audit. |
| tokens-resets | Backed as is, with an outside source (costs page): /compact summarises the conversation. |
| tokens-readings | Reworded twice: "every phase boundary" became "every phase start and before and after every reset" (finding 5), then exceptions are named from the data (finding 11). |
| tokens-checks | Backed as is: one pipeline test per check. |

Removed: none. Every factual paragraph, list item and definition on the five pages is either in
this register or inside an area that names the file it is drawn from, and a recorded test fails
otherwise.
