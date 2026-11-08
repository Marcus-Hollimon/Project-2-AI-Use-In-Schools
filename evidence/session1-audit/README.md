# Session 1 audit: errors in Claude's first analysis, and the check that caught them

On 2026-11-08 at 00:00 EST Claude inspected the Claude Code transcripts in
`~/.claude/projects/C--Claude-Folder/` and reported token totals and a `/clear` event. When Marcus
asked for a review of the work so far (00:15 EST), Claude wrote `audit.py` to re-check its own
claims. Output: `audit-output.txt` (token counts per session only; no conversation content).

| First claim | Audit result |
|---|---|
| Largest session: 4,504,003,024 cache-read tokens vs 13,906,348 output | Wrong, about 2x too high. Each API response is saved as several rows that repeat the same usage. 12,131 rows, 5,733 responses. Deduplicated: 2,177,396,715 vs 5,514,253 (ratio 395 to 1). |
| Session files can be summed | Wrong. 316 responses appear in two or more files: resuming a session copies its history into a new file. |
| A 04:51 / 04:52 gap between two files was a `/clear` | Wrong. 1,362 of the second file's 1,364 rows were copied from the first, so it was a resumed session. |
| `/compact` is recorded in transcripts | Confirmed: 25 rows flagged `isCompactSummary`, all `true`. |

Consequence for the project: every token figure is deduplicated by response id, within and across
files (rule in `CLAUDE.md`). How `/clear` appears in the data is tested directly in Phase 1.

Re-run: `python -I evidence/session1-audit/audit.py`. It reads the local transcripts, so numbers
grow as more sessions are added; the committed output is the 2026-11-08 snapshot.
