# State: read this first

Current phase: 1 Instrumentation (not started; write its spec first)

Last updated: 2026-11-08T00:45-05:00 by Claude, at the end of Phase 0.

## Where things stand
- Phase 0 Foundation: done, except Marcus's checklist in `specs/phase-0-foundation.md`.
- Live site (skeleton only): https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Tests: 17, all passing. Recorded runs in `validation/runs/`, including 2 deliberate mutation runs.
- Budget at Phase 0 end: weekly 52% used (resets Tue Nov 10 01:00 EST); 5-hour window 25%.

## Next: Phase 1 Instrumentation
1. Write `specs/phase-1-instrumentation.md` before any code.
2. A Python script (run with uv) that reads this project's transcripts and produces deduplicated
   data for the Contributions and Token usage tabs. Dedup rules: `evidence/session1-audit/`.
3. Find out how `/clear` really appears in the transcripts: Marcus runs `/clear` at a known moment,
   then we inspect what changed on disk.
4. Cross-check token totals against an independent number (the app's context reading).

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38, then claude-opus-5-5 | planning, audit, Phase 0 |

Start new sessions in `C:\Claude Folder\Project-2-AI-Use-In-Schools` so their transcripts land in
their own folder. Add each new session to this table.

## Open decisions (Marcus)
- Final sample size: after the Phase 2 pilot measures cost per school.
- Whether bulk research may use a cheaper model: measure it in the pilot first.

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. Write one file per command; keep backslash escapes out of code.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
