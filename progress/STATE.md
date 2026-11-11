# State: read this first

Current phase: 2 Study (spec written, frame built, 15 schools drawn; WAITING for Marcus's approval)

Last updated: 2026-11-11T10:08:06-05:00 by Claude (session a9056776).

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
- Phase 2 spec written: `specs/phase-2-study.md`. Frame built and 15 schools drawn
  (`data/frame/`, seed 20261111 committed in `405f8dd` before the run).

## Next: Phase 2 Study (waiting for Marcus's approval of `specs/phase-2-study.md`)
- The spec is the plan. Its "Questions for Marcus" are the open items (design and list, blind
  check on 3 schools, cheaper model).
- The pre-clear design here said CIP 11.07 only; that would have excluded Ohio State and
  Cincinnati. Replaced by 11.0701 or 11.0101 (spec, "Known before any coding" item 3).
- On approval: change the project spec's "10 hand-coded schools" to 3 (if he agrees), write
  `study/codebook.md`, then the 5-school pilot.

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
