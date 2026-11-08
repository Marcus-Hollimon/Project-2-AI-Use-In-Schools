# Phase 0: Foundation

Goal: everything later phases stand on, and proof that publishing to the web works, before any
real content exists.

## Tasks
1. Remove the retired canon-keeper hook from `C:\Claude Folder\.claude\settings.json`
   (backup in `~/.claude/backups/`).
2. Project `CLAUDE.md`, this spec, the project spec, the progress files.
3. React skeleton in `web/`: an Overview plus four tabs, one per deliverable, numbered as in the
   assignment. Navigation uses the part of the address after `#` (for example `#/tokens`), so
   GitHub Pages only ever serves one file. That is what makes a hard refresh safe.
4. Tests with Vitest and Testing Library. Every run saved to `validation/runs/` with time and commit.
5. GitHub Actions deploy, taken from Vite 8.3.6's own docs
   (`reference/vite-v8.3.6/docs/guide/static-deploy-github-pages.yaml`), adapted for `web/`, with
   lint and tests before the build so a failing test blocks deployment.
6. Every page shows the commit it was built from.

## Acceptance checks
Claude runs these and records the results:
- [x] Lint passes. Build passes. Tests pass, and the run is saved in `validation/runs/`.
- [x] Built `index.html` loads its files from `/Project-2-AI-Use-In-Schools/`.
- [x] The GitHub Actions deploy run succeeds.
- [x] The live address and its JavaScript file both answer HTTP 200.
- [x] In a real browser, each of the five pages shows the right heading after a reload, with no
      console errors.

Marcus's checklist (do it yourself, then tick and date each line):
- [x] Open the live site. It loads.
- [x] Click each of the four numbered tabs. Each shows its own title.
- [x] On the Token usage tab, press Ctrl+F5. You are still on Token usage.
- [x] The commit code in the page footer matches the latest commit on the GitHub repo page.
- [x] On GitHub, you can find `specs/`, `progress/`, and `validation/`.

## Results (Claude, 2026-11-08)
- Lint clean, build clean, 17/17 tests recorded. Two deliberate mutation runs show the tests fail
  when the app is broken.
- Built and live `index.html` load every file from `/Project-2-AI-Use-In-Schools/`; each answers 200.
- Deploy run 42451739541 succeeded in 27 s.
- Each deliverable page renders correctly on a proven fresh page load, with no console errors.
  Limit: reload keys cannot be pressed in Claude's browser pane, so the keystroke itself is in
  Marcus's checklist. Details: `validation/manual-checks.md`.
- Phase 0 cost: 5-hour window 15% to 25%, weekly limit 51% to 52%.
