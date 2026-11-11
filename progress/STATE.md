# State: read this first

Current phase: 1 Instrumentation (complete; the deliberate `/clear` that ends it is next or just happened)

Last updated: 2026-11-11T09:52-05:00 by Claude, just before the `/clear`.

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

## FIRST, right after the /clear (end of Phase 1, spec section "End of phase")
1. Usage reading marked "after /clear" in `progress/usage.md` (tool: get_usage).
2. Find how the `/clear` shows up. Look in `~/.claude/projects/C--Claude-Folder/` for `.jsonl`
   files changed after 09:52 EST Nov 11. Do not open any file without first checking, from its
   first few records only, that its `cwd` is this project or `C:\Claude Folder` and its time is
   after the clear. Expect either a new session file or a marker inside
   `0cf9c9ad-b66c-4406-998d-e6e34b8c2e47.jsonl`. Record what you find in the log and the spec.
3. If there is a new session id, add it to `pipeline/sessions.json` as the last (live) entry, then
   run `uv run --project pipeline python pipeline/build.py`. All checks must still pass.
4. Unknown file: `ddc7d76a-46ca-4bba-a89a-f901ccc7b9a7.jsonl` in the same folder, last written
   Nov 8 18:00. Not opened (privacy). Ask Marcus whether it belongs to this project.
5. Commit, push, then write `specs/phase-2-study.md` (below) and get Marcus's approval.

## Next: Phase 2 Study (15 schools)
Marcus's decision (Nov 11): 15 schools, popular Ohio schools plus some big national names, Harvard
named as an example. This is a chosen sample: findings describe these 15 only. Proposed list, to be
confirmed by Marcus in the Phase 2 spec:
- Ohio (10): Ohio State, Cincinnati, Case Western Reserve, Miami University, Ohio University,
  Kent State, Dayton, Bowling Green State, Toledo, Wright State.
- National (5): Harvard, MIT, Stanford, Carnegie Mellon, UC Berkeley.
Spec outline: codebook written before any coding (stance on genAI: encourage, permit, restrict,
mixed, none found; tone; whether collaboration with AI is discussed; how software engineering
courses handle it; source type). Save the raw page behind every coded value with `curl` into
`data/sources/<school>/<date>-<name>.html` (real bytes, not a summary). One row per school in
`data/coded/`. Marcus hand-codes a few schools blind; compute agreement. Then Phase 3 (tabs).

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38 Nov 8, then claude-opus-5-5 | planning, audit, Phase 0, first /compact (Nov 8 00:57), Phase 1, ends with the /clear |

## Open decisions (Marcus)
- Confirm or change the 15-school list (in the Phase 2 spec).
- Whether bulk research may use a cheaper model.

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. A single long prose heredoc also failed. Write prose and Markdown with the file-writing
  tool; keep backslash escapes out of code.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
- The Claude app shows Marcus no context-token number. Never write a checklist step that needs one.
