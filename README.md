# How US computer science departments talk about generative AI

A small study of generative-AI policy in US computer science departments, built with **agentic
development**: Claude Code wrote the code, and Marcus Hollimon supervised through specs, tests,
and reviews. Class project (Project 2), November 2026.

**Live site:** https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/

## Status
Phase 0 (foundation) of 5. Current state: [`progress/STATE.md`](progress/STATE.md).

## Where things are
| Folder | What it holds |
|---|---|
| [`specs/`](specs/) | What each phase must deliver and how it is checked |
| [`progress/`](progress/) | Timestamped log, Marcus's decisions, plan-usage readings, current state |
| [`validation/`](validation/) | Every recorded test run, and manual review steps |
| [`evidence/`](evidence/) | Scripts and outputs behind claims made in the log |
| [`web/`](web/) | The website (React 19, Vite 8), deployed by GitHub Actions on every push to `main` |

## Run the site locally (Windows PowerShell)
```powershell
cd web
npm install
npm run dev
```
