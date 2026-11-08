# Project 2: How US CS departments talk about generative AI

**Read `progress/STATE.md` first in every new or cleared session.** It says which phase we are in,
what is done, and what is next. The project-wide spec is `specs/00-project.md`. Work only against
the current phase spec in `specs/`, and write a phase's spec before starting that phase.

## Roles (decided 2026-11-08)
- Claude writes the code, including the UI. Marcus supervises through specs, tests, and reviews.
- Marcus reviews behavior through the checklist in each phase spec, not by reading code. Write
  those checklists so a non-programmer can follow them.

## Layout
- `specs/`: project spec, one spec per phase
- `progress/`: `STATE.md` (where we are), `log.md` (timestamped milestones), `decisions.md`
  (Marcus's decisions), `usage.md` (plan-limit readings at phase boundaries)
- `web/`: React app (Vite 8.3, React 19.3, Vitest 5.1, oxlint). `.github/workflows/deploy.yml`
  deploys it to GitHub Pages on every push to `main`.
- `validation/`: `runs/*.json` (every recorded test run) and `manual-checks.md` (browser and
  human review steps)
- `evidence/`: scripts and outputs that back claims made in the log
- `reference/`: pinned sparse clones of third-party docs at the versions we use. Gitignored.

## Rules
- Update `progress/log.md` at every milestone and `progress/STATE.md` before any context reset.
  Timestamps: ISO 8601 with offset, Eastern time (`date -Iseconds` in Git Bash).
- Every phase start and end: record a reading in `progress/usage.md` (5-hour %, weekly %, context
  tokens) and note how context was reset (new session, `/clear`, `/compact`).
- Run web tests with `npm run test:record` in `web/`, which saves the run to `validation/runs/`.
  Never report a test result that was not recorded.
- Pipeline (Phase 1): from the repo root, `uv run --project pipeline python pipeline/build.py` rebuilds
  `data/derived/` from the sessions in `pipeline/sessions.json` (add each new session id there), and
  `uv run --project pipeline python pipeline/record_tests.py "label"` records a pipeline test run.
- Token accounting: transcripts repeat the same usage on every row of one API response, and
  resumed sessions copy history into new files. Deduplicate by response id, within and across
  files. Never sum rows. Evidence: `evidence/session1-audit/`.
- Privacy: never commit raw transcripts or anything from other projects. Publish only derived
  data, and prompts from this project's sessions after Marcus has reviewed them.
- Research data: save the raw source page (date-stamped) behind every coded value, so any data
  point can be checked against its source.
- Third-party APIs: read `reference/` at the installed version before writing code against them.
- Commands handed to Marcus must work in Windows PowerShell 5.1.
- Bash tool quirk seen 2026-11-08: several heredocs in one command failed to parse. Write one
  file per command. Double backslashes also collapse to one: keep backslash escapes out of code,
  and run lint after writing. A single long prose heredoc also failed (01:00): write Markdown and
  prose files with the file-writing tool.

## Context resets (decided 2026-11-08)
- Marcus prefers `/compact` over `/clear`. Claude has no tool to run `/compact`; only Marcus can
  type it (auto-compact fires only at 97% of a 1M window, far too late for the budget).
- At each good boundary (phase end, or a big chunk done): update `STATE.md`, commit, record a usage
  reading marked "just before /compact", then give Marcus the exact `/compact <focus text>` line.
- First thing after a compact: take a usage reading marked "after /compact".
