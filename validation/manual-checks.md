# Manual and browser checks

Checks that are not automated tests: done by Claude in a real browser, or by Marcus by hand. Each
entry says who did it, when, what was checked, and what was observed, including what did not work.

## Phase 0: live site, 2026-11-08

Site: https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/ built from commit `b945d66`
by GitHub Actions run 42451739541 (00:41:15 to 00:41:47 EST, success, 27 s).

### C1. Network check (Claude, 00:42 EST, curl)
| Request | Result |
|---|---|
| Live page | HTTP 200, 701 bytes |
| `/Project-2-AI-Use-In-Schools/favicon.svg` | 200 |
| `/Project-2-AI-Use-In-Schools/assets/index-DQBF798U.js` | 200 |
| `/Project-2-AI-Use-In-Schools/assets/index-DiuQjaG2.css` | 200 |
| Commit string inside the live JavaScript | `b945d66`, same as repository `main` |

### C2. Each page in a real browser (Claude, 00:42 to 00:43 EST, Claude Code browser pane)
Method: before each load, set a marker variable in the page; load the page's address; a fresh page
load erases the marker. Then read the page heading and the highlighted tab.

| Address | Fresh page load proven | Heading shown | Highlighted tab |
|---|---|---|---|
| `?fresh=11#/research` | yes | Research findings | 1. Research findings |
| `?fresh=12#/validation` | yes | Validation evidence | 2. Validation |
| `?fresh=13#/contributions` | yes | Timeline and contributions | 3. Contributions |
| `?fresh=14#/tokens` | yes | Token usage | 4. Token usage |
| `/` (overview) | loaded, not marker-checked | How US computer science departments talk about generative AI | Overview |

Console errors across all loads: none. Overview footer: "Built from commit b945d66".

### C3. What did not work, and why it matters
- **The first attempt at C2 proved less than it seemed.** Moving between `#` addresses on one page
  does not load a fresh page, and the page-load type read `navigate` every time, never `reload`.
  Claude's own check flagged it; the marker method above replaced it.
- **The marker was first set only once**, so "marker gone" proved a fresh load for the first page
  only. Fixed by setting it before every load; the table above is the corrected run.
- **Reload keys do not reach Claude's browser pane.** After F5 the marker was still present, so no
  reload happened; Ctrl+Shift+R also produced none. A refresh is a fresh load of the same address,
  and GitHub Pages receives the same request for every page (the part after `#` never reaches the
  server), so C2 covers the refresh case. The keystroke itself is checked by Marcus (M1).

## Marcus's checks

### M1. Phase 0 checklist (to do)
Steps: `specs/phase-0-foundation.md`, "Marcus's checklist". Record here the date and time, what
you saw, and anything that looked wrong.
