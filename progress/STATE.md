# State: read this first

Current phase: 1 Instrumentation (not started; write its spec first)

Last updated: 2026-11-08T00:53-05:00 by Claude, at the end of Phase 0.

## Where things stand
- Phase 0 Foundation: done. Marcus's checklist passed 5/5 at 00:51.
- Live site (skeleton only): https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Tests: 17, all passing. Recorded runs in `validation/runs/`, including 2 deliberate mutation runs.
- Budget just before the first `/compact`: weekly 53% (resets Tue Nov 10 01:00 EST), 5-hour 28%.

## How context is reset
`/compact`, typed by Marcus at boundaries Claude prepares (see CLAUDE.md). After any compact, take
a usage reading first and add it to `progress/usage.md` as "after /compact".

## Next: Phase 1 Instrumentation
1. Write `specs/phase-1-instrumentation.md` before any code.
2. A Python script (run with uv) that reads this project's transcripts and produces deduplicated
   data for the Contributions and Token usage tabs. Dedup rules: `evidence/session1-audit/`.
3. Find how the first `/compact` (about 00:54 on Nov 8) appears in the transcript, using the
   `isCompactSummary` and `compactMetadata` fields seen in the audit.
4. Cross-check token totals against an independent number (the app's context reading).

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38, then claude-opus-5-5 | planning, audit, Phase 0, continues after compaction |

## Open decisions (Marcus)
- One deliberate `/clear` for deliverable 4's clear-vs-compact comparison, or compact only.
- Final sample size: after the Phase 2 pilot measures cost per school.
- Whether bulk research may use a cheaper model: measure it in the pilot first.

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. Write one file per command; keep backslash escapes out of code.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
