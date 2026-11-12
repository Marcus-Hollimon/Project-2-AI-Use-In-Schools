# Phase 6 spec: evaluation, "how the tests work", presentation

Status: DRAFT for Marcus's approval (written 2026-11-11 after the Phase 5 /compact). No Phase 6 work
starts until Marcus approves.

## The idea in one paragraph
Tests cannot prove that they cover every edge case: no test suite anywhere can, because "every
edge case" is not a list anyone can write down. Claiming it in the presentation would be false, and
a grader who knows testing would catch it. What this project *can* show, with evidence already in
the repo, is stronger and honest: every sentence on the site is tied to a test or a saved source,
the tests were deliberately broken to prove they catch errors, they caught 15 real errors, and the
places they cannot reach are named. Phase 6 explains that on the site and turns it, with the
findings, into a PowerPoint deck.

## Budget first (a decision for Marcus)
Usage at 20:53 EST: 5-hour window 37%, weekly 38%. The stop rule says stop at 40% weekly. Phase 5's
last task alone moved weekly by 2 points, so Parts A and B below will very likely cross 40%. Marcus
chooses one:
1. Raise the weekly stop line (for example to 50%) for Phase 6 only. Extra usage is off, so the real
   hard stop is 100%.
2. Keep 40%: Claude does Part B (the deck) only, with a shorter Part A folded into the deck.

## Part A: a "How the tests work" section on the Validation tab
A new section at the top of the Validation tab, in plain language, every number computed from repo
files (as everywhere else on the site):

1. **Three layers, one picture.** The study checks test the *data* (S1 to S5, C1 to C4, N1 on all 36
   schools); the unit tests test the *code* that does the checking and counting (study 42, pipeline
   19); the site tests test *what the pages say* (web 49). The claims register (26 claims) ties each
   sentence on the site to one of those.
2. **How we know a test can catch an error.** Each "mutation run" deliberately breaks one rule and
   records that its test then failed (pipeline check C6 lists them). This is the honest answer to
   "how do you know the tests work": they were shown to fail when the thing they guard was broken.
3. **What the tests caught.** The 15 entries in `validation/caught.json`, with a count.
4. **Edge cases, by rule.** A table built from the test names: for each check rule, the cases tested
   (passes when right, fails when wrong, the "none found" and empty-page cases, and so on). This shows
   *which* edge cases are covered, instead of claiming all of them are.
5. **What no test here can prove.** Named plainly:
   - whether a tone or stance is the *right reading* of a page (the tests prove the quote is real,
     word for word, and fits the codebook's cue words, not that a second person would agree; no
     second coder was used, by Marcus's decision);
   - anything about schools outside the 36 (the groups are too small to generalize);
   - pages behind logins, and pages that change after coding (the re-fetch report covers the last).

Optional, only if budget allows (Marcus chooses): run a mutation-testing tool over `check_study.py`.
It makes hundreds of small automatic bugs and reports the share the tests catch (a "mutation score"),
plus every bug they miss. It is the closest thing to a measured answer to "how complete are the
tests", but the misses it finds would need fixing or listing, which costs time and usage.

## Part B: the presentation deck (.pptx)
About 12 slides, saved as `presentation/AI-in-CS-departments.pptx`, every number read from the repo
by a script (not typed), with speaker notes for Marcus on each slide.

1. Title, Marcus's name, site link
2. The question (from the assignment)
3. How the schools were chosen: 30 national in 5 strata, 6 Ohio, reported apart
4. How each answer was coded: codebook, quote, saved copy, link that opens the live page at the quote
5. Finding: CS departments with no AI statement of their own
6. Finding: university stances (national and Ohio side by side, as counts, chart)
7. Finding: disclosure required, split into "stated outright" and "read from a plagiarism rule"
8. Finding: tone of university pages, and that most software engineering syllabi are not public
9. How we proved it: the three layers and the claims register
10. How we know the tests work: mutation runs and the 15 errors caught; what tests cannot prove
11. The process: spec per phase, Marcus's decisions (judgment calls, codebook v3), contributions
    timeline, token usage and the /compact vs /clear comparison
12. Limits and what we would do next; links to the site and repo

Deliverables E (evaluation) and R (reflection) stay Marcus's to write (project spec). The deck gives
them one slide each with his headings and no text from Claude; Claude supplies numbers on request.

## What Claude will not do
- Claim the tests are exhaustive, or that the findings describe all US departments.
- Type a number into the deck or the site by hand.
- Change any coded value (Phase 5 is closed).

## Exit check (Marcus)
Plain-language checklist, done on the live site and in PowerPoint:
- [ ] The Validation tab opens with "How the tests work", and I can explain the three layers from it.
- [ ] The section says plainly what the tests cannot prove.
- [ ] Every number in the deck matches the site (spot-check three).
- [ ] The deck opens in PowerPoint, the charts are readable, and every slide has speaker notes.
- [ ] My evaluation and reflection slides are mine.
- [ ] All tests pass, recorded, and the site shows the new commit.
