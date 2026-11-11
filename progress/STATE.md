# State: read this first

Current phase: 2 Study (pilot: 3 of 5 schools coded and passing; Coppin State and Snow are next)

Last updated: 2026-11-11T10:42:58-05:00 by Claude (session a9056776), just before the second `/compact`.

## Deadline and pace
- Everything is due **2 PM EST, Thu Nov 12 2026** (Marcus, 2026-11-11).
- Weekly limit 10% (resets Tue Nov 17 01:00 EST). **The 5-hour window is the real constraint**:
  it went 10% to 22% from 10:00 to 10:21 Nov 11 while context grew 78k to 198k. It resets 14:40 EST.
- Marcus wants a `/compact` prepared at every phase end and after each big chunk (CLAUDE.md).
- Marcus asked (10:15 Nov 11): **no Coaching sections** any more, despite the global CLAUDE.md
  rule and the per-turn hook; and no plan mode. "Let's just try and get this done properly."

## FIRST, right after the /compact
1. Take a usage reading marked "after /compact" in `progress/usage.md` (tool: get_usage), with the
   time from `date -Iseconds`. Run `uv run --project pipeline python pipeline/build.py`; C1 to C3 must pass.
2. Continue the pilot: Coppin State 162283 (coppin.edu), then Snow 230597 (snow.edu). Same procedure
   as below. Then do the "After the 5" step.

## Pilot so far (details and costs in `progress/pilot-cost.md`)
- Minnesota 174066, Johns Hopkins 162928, Valparaiso 152600: coded, all pass `check_study.py`;
  committed and pushed (116489e has the first two). Average 3.3 five-hour points and about 41,500
  tokens of context per school; 5-hour was 34% at 10:42, resets 14:40 EST.
- Check S3 changed during the pilot: browser text (`--rendered`) passes with a raw curl copy at
  HTTP 200, or at HTTP 403 plus a written `fetch_reason` on the value (spec and test updated; sabotage
  run failed exactly the new test). Not yet needed by any coded value.
- `.gitattributes` now stores `data/sources/**` byte-for-byte (`-text`); without it git rewrote line
  endings in archives, which would break S2 hashes on a fresh checkout.
- Codebook v2 candidates (pre-2023 course pages; example syllabus language for disclosure; department
  news as department text) are listed in `pilot-cost.md`. Decide after school 5; if adopted, recode the
  pilot schools (spec R2).
- Helpers that worked: a scratch text viewer (`showtext.py` in the session scratchpad: prints a saved
  page's visible text, filtered by a regex) and `pdftotext -enc UTF-8 <pdf> <pdf>.txt` for the PDF
  sidecar. Filter page text by regex rather than printing whole pages; it keeps context growth down.
- Do NOT retry curl with extra browser headers when a site returns 403: the permission system refused
  it as bot-check circumvention. Read such pages in the browser pane instead.
- ddc7d76a: checked with Marcus's permission (metadata only); it is the retired canon-keeper project
  (Sep 9), not this one. Closed.

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
- Tests: study 31/31 (mutation run with S2 disabled failed exactly the S2 test; restored), pipeline
  12/12, web 17/17; all recorded. CI runs all three suites before deploy (pushed 5ccc209).

## Pilot: how to code one school (spec task 4)
Schools, one per stratum: Minnesota 174066 (umn.edu), Johns Hopkins 162928 (jhu.edu), Valparaiso
152600 (valpo.edu), Coppin State 162283 (coppin.edu), Snow 230597 (snow.edu).
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
   `{"codebook_version": 1, "schools": [{"unitid", "slug", "name", "values": {var: entry}}]}`.
   Entry with evidence: value, quote, url, archive (repo-relative path), source_type, optional
   cue_reason, optional domain_reason. Absence entry: value plus `reviewed` (list of archive paths)
   or `search_log` (path). For every "none found" or "no public syllabus found", also run and log
   the 2 `second_searches`.
5. Run `check_study.py --only <unitid>`; fix until it passes. Note time and a get_usage reading per
   school in `progress/pilot-cost.md` (time taken, 5-hour points, context growth).
After the 5: report cost per school and the projection for 15 against the deadline and the
5-hour window; change the codebook only as version 2 with reasons (spec R2); prepare a /compact.

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
