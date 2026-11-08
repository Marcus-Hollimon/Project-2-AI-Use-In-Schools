# State: read this first

Current phase: 1 Instrumentation (Claude's checks all done; waiting for Marcus's checklist)

Last updated: 2026-11-08T01:30-05:00 by Claude.

## Where things stand
- Phase 0 Foundation: done. Marcus's checklist passed 5/5 at 00:51.
- Phase 1: tasks 1 to 8 done (commit be9164a, CI run 42454962332 green incl. 12 pipeline tests).
  Pipeline in `pipeline/`, output in `data/derived/`, all cross-checks pass. Marcus chose
  "publish all" for Q&A. C2 was amended once (unanswered retry request); see the spec.
- Live site (skeleton only): https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Tests: web 17/17, pipeline 12/12, all recorded in `validation/runs/` with 4 mutation runs total.
- Budget at 01:30: weekly 54% (resets Tue Nov 10 01:00 EST), 5-hour 42% (resets 04:30 EST).
  Phase 1 so far: 11 five-hour points, 1 weekly.

## How context is reset
`/compact`, typed by Marcus at boundaries Claude prepares (see CLAUDE.md). After any compact, take
a usage reading first and add it to `progress/usage.md` as "after /compact".
Planned exception (decided by Marcus 2026-11-08): one deliberate `/clear` at the end of Phase 1, so
deliverable 4 can compare clear with compact. Before it: commit, update STATE.md, usage reading.

## Next: Phase 1 Instrumentation
1. Marcus does the 4-item checklist in `specs/phase-1-instrumentation.md`; Claude records it.
2. End of phase: the deliberate `/clear`, steps listed at the end of the spec.

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38, then claude-opus-5-5 | planning, audit, Phase 0, continues after compaction |

## Open decisions (Marcus)
- Final sample size: after the Phase 2 pilot measures cost per school.
- Whether bulk research may use a cheaper model: measure it in the pilot first.

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. Write one file per command; keep backslash escapes out of code. At 01:00 a single heredoc
  (the Phase 1 spec, about 100 lines of prose) also failed to parse; cause not identified. Write
  prose and Markdown files with the file-writing tool, not a shell heredoc.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
