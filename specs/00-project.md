# Project spec: How US computer science departments talk about generative AI

Owner: Marcus Hollimon. Builder: Claude Code. Approved for Phase 0 by Marcus on 2026-11-08.

## Purpose
Two goals, graded together:
1. **A small research study.** How US computer science departments permit, encourage, or restrict
   generative AI; whether their official publications take a positive view and discuss
   collaborating with AI; how software engineering courses handle it.
2. **A demonstration of agentic, spec-driven development.** Claude writes the code; Marcus
   supervises through specs, tests, and reviews; both contributions are documented.

## Deliverables (numbered as in the assignment)
| # | Deliverable | Lives in | Done when |
|---|---|---|---|
| 1 | Study data, analysis approach, findings dashboard | `data/`, tab "Research findings" | 36 schools (Phase 5, Marcus 2026-11-11; was 15): 30 drawn at random within 5 strata nationally (6 each), plus 6 Ohio (Ohio State and Cincinnati fixed), Ohio reported separately. Codebook written before coding. Every coded value links to an archived source page. Findings compare institution types, labeled as descriptive (groups are small). |
| 2 | Validation viewer | `validation/`, tab "Validation" | Every recorded test run since Phase 0 is searchable and filterable by phase, status, and name. Includes the study checks (sources real and unchanged, coding rules applied, "none found" re-searched; see `specs/phase-2-study.md`) and the errors that checks caught. No hand-coding (Marcus, 2026-11-11). |
| 3 | Contributions and timeline | `progress/`, tab "Contributions" | Timeline built from `progress/` and this project's transcripts. Each entry attributed to Marcus or Claude. Marcus's questions and Claude's responses viewable. |
| 4 | Token usage | `progress/usage.md` plus derived data, tab "Token usage" | Figures deduplicated. Four token classes shown separately. Plan-limit readings at every phase boundary. At least one `/clear` and one `/compact` at known moments, compared. |
| E | Evaluation against goals | written by Marcus | Marcus writes it; Claude supplies numbers on request. |
| R | Reflection: agentic vs AI-assisted | written by Marcus | Marcus writes it. |
| P | Published on GitHub and the web | this repo, GitHub Pages | Site rebuilds from `main` automatically. Each page shows the commit it was built from. |

## Constraints
- Deadline: everything by 2 PM EST, Thu Nov 12 2026 (Marcus, 2026-11-11; replaces the earlier
  Nov 10, 11, 12 split).
- Budget: Claude Pro. Weekly limit 8% used on Nov 11 09:46; resets Tue Nov 17 01:00 EST.
  Extra usage is off, so hitting the limit is a hard stop until the reset.
- Marcus reviews behavior through checklists, not code.
- Raw transcripts are never published.

## Phases
| Phase | Produces | Exit check |
|---|---|---|
| 0 Foundation | Repo structure, CLAUDE.md, specs, progress files, React skeleton live on GitHub Pages | Live site: all tabs load and survive a hard refresh. Tests recorded. Marcus completes the Phase 0 checklist. |
| 1 Instrumentation | Scripts turning this project's transcripts into deduplicated data for tabs 3 and 4 | Totals cross-checked against an independent number. Tests recorded. |
| 2 Study | Codebook, sample frame, 5-school pilot, measured cost per school, final N, coded data with archived sources, automated study checks | Every coded value has a source. All study checks pass. |
| 3 Interfaces | The four tabs filled with real data | Marcus's checklist per tab |
| 4 Validation | Validation tab complete, evidence review | Any claim on the site traces to a test or a source. |
| 5 More schools | 21 more schools coded the same way (`specs/phase-5-more-schools.md`; added by Marcus 2026-11-11) | All study checks pass on 36 schools; Marcus's checklist |
| 6 Evaluation | Marcus's evaluation, reflection, presentation | Marcus |

At every phase boundary: usage reading, `STATE.md` update, context reset, and a note of which reset.

## Out of scope
- Any live server or database. The site is static and built from files in this repo.
- Data behind logins (LMS pages, private syllabi).
