# State: read this first

Current phase: 1 Instrumentation (spec written, waiting for Marcus's approval; no code yet)

Last updated: 2026-11-08T01:03-05:00 by Claude, after the first `/compact` (00:57:16).

## Where things stand
- Phase 0 Foundation: done. Marcus's checklist passed 5/5 at 00:51.
- Phase 1: spec at `specs/phase-1-instrumentation.md`; recon behind it in `evidence/phase1-recon/`.
- Live site (skeleton only): https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Tests: 17, all passing. Recorded runs in `validation/runs/`, including 2 deliberate mutation runs.
- Budget after the first `/compact`: weekly 53% (resets Tue Nov 10 01:00 EST), 5-hour 31%
  (resets 04:30 EST). Context 81,551 tokens, of which about 78k is fixed overhead.

## How context is reset
`/compact`, typed by Marcus at boundaries Claude prepares (see CLAUDE.md). After any compact, take
a usage reading first and add it to `progress/usage.md` as "after /compact".
Planned exception (decided by Marcus 2026-11-08): one deliberate `/clear` at the end of Phase 1, so
deliverable 4 can compare clear with compact. Before it: commit, update STATE.md, usage reading.

## Next: Phase 1 Instrumentation
1. Marcus approves (or changes) `specs/phase-1-instrumentation.md`. No pipeline code before that.
2. Then work through the spec's Tasks 1 to 8 in order, and its acceptance checks.
3. End of phase: the deliberate `/clear`, steps listed at the end of the spec.

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
