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
- [ ] Lint passes. Build passes. Tests pass, and the run is saved in `validation/runs/`.
- [ ] Built `index.html` loads its files from `/Project-2-AI-Use-In-Schools/`.
- [ ] The GitHub Actions deploy run succeeds.
- [ ] The live address and its JavaScript file both answer HTTP 200.
- [ ] In a real browser, each of the five pages shows the right heading after a reload, with no
      console errors.

Marcus's checklist (do it yourself, then tick and date each line):
- [ ] Open the live site. It loads.
- [ ] Click each of the four numbered tabs. Each shows its own title.
- [ ] On the Token usage tab, press Ctrl+F5. You are still on Token usage.
- [ ] The commit code in the page footer matches the latest commit on the GitHub repo page.
- [ ] On GitHub, you can find `specs/`, `progress/`, and `validation/`.
