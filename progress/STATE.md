# State: read this first

Current phase: 2 Study (spec being written; not yet approved)

Last updated: 2026-11-11T10:02:48-05:00 by Claude (session a9056776, after the /clear).

## Deadline and pace
- Everything is due **2 PM EST, Thu Nov 12 2026** (Marcus, 2026-11-11).
- Budget is not the constraint: weekly 8% at 09:46 Nov 11 (resets Tue Nov 17 01:00 EST).
- Marcus wants a `/compact` prepared at every phase end and after each big chunk (CLAUDE.md).

## Where things stand
- Phase 0 Foundation: done (Marcus 5/5, Nov 8 00:51).
- Phase 1 Instrumentation: done. Claude's 5 checks and Marcus's 4 passed (Nov 11 09:50; one
  item replaced, see the spec). Pipeline in `pipeline/`, output in `data/derived/`. Q&A: Marcus
  chose "publish all" and found the preview fine.
- Live site is still a skeleton: https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Tests: web 17/17, pipeline 12/12, all recorded in `validation/runs/` (4 mutation runs total).
- Work paused Nov 8 01:30 to Nov 11 09:46 (Marcus away). Not a context reset: same session.

## After the /clear (done 2026-11-11 10:02, session a9056776)
- Reading "after /clear" taken (78,618 tokens; C1 passes, 15 apart).
- The `/clear` started a new session and file; neither file records the clear (spec 1, item 8).
- `a9056776` added to `pipeline/sessions.json`; build all PASS; tests 12/12 recorded.
- Still open: `ddc7d76a-46ca-4bba-a89a-f901ccc7b9a7.jsonl` (same folder, last written Nov 8 18:00,
  while Marcus was away). Not opened (privacy). Asked Marcus whether it belongs to this project.
- Next: write `specs/phase-2-study.md` (below) and get Marcus's approval.

## Next: Phase 2 Study (15 schools)
Marcus's decision (Nov 11, 09:58, replacing his 09:51 hand-picked list): stratified, to reach "US
CS departments" as far as 15 schools can; Ohio included because he lives there; Ohio State and
University of Cincinnati must be in it; the design is left to Claude. Claude's design (put it in the
Phase 2 spec for his approval):
- **Frame**: US degree-granting institutions that award computer science degrees (CIP 11.07),
  from the federal IPEDS data files (institution file plus completions file, latest year). Download
  the raw files, archive them in `data/frame/`, and record their URLs and dates. Verify the
  Carnegie classification field names from the files themselves, never from memory.
- **Strata (5)**, by Carnegie basic classification and control: public R1; private R1; other
  doctoral and master's universities; baccalaureate (liberal arts) colleges; associate's
  (community) colleges.
- **National sample (10)**: 2 per stratum, drawn at random with a recorded seed, excluding Ohio.
  Record each school's region so the spread is visible.
- **Ohio oversample (5)**: Ohio State and Cincinnati fixed (Marcus), plus 3 Ohio schools drawn at
  random, one each from the master's, baccalaureate, and associate's strata.
- **Reporting**: national 10 by stratum, Ohio 5 separately; never pooled into one "US" percent.
  With 2 per stratum the findings are illustrative, not estimates, and the site says so.
- Harvard (mentioned earlier by Marcus) is in only if the draw picks it. Hand-adding it would make
  private R1 a chosen pick again; ask Marcus only if he raises it.
- Fallback if IPEDS cannot be downloaded and filtered within about 30 minutes: hand-pick within
  the same strata and label the sample as hand-picked.
Spec outline: codebook written before any coding (stance on genAI: encourage, permit, restrict,
mixed, none found; tone; whether collaboration with AI is discussed; how software engineering
courses handle it; source type). Save the raw page behind every coded value with `curl` into
`data/sources/<school>/<date>-<name>.html` (real bytes, not a summary). One row per school in
`data/coded/`. Marcus hand-codes a few schools blind; compute agreement. Then Phase 3 (tabs).

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38 Nov 8, then claude-opus-5-5 | planning, audit, Phase 0, first /compact (Nov 8 00:57), Phase 1, ends with the /clear |
| a9056776-4951-4636-a9ad-acb1dbccb955 | `C:\Claude Folder` (same folder) | claude-opus-5-5 | starts after the /clear (Nov 11 10:00:07); Phase 2 |

## Open decisions (Marcus)
- Approve the sampling design and the drawn list (in the Phase 2 spec).
- Whether bulk research may use a cheaper model.

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. A single long prose heredoc also failed. Write prose and Markdown with the file-writing
  tool; keep backslash escapes out of code.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
- The Claude app shows Marcus no context-token number. Never write a checklist step that needs one.
