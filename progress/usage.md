# Plan usage readings

Read from the Claude app's own usage data (the same numbers as its usage card) at phase
boundaries. Pro plan. The weekly limit resets Tue 2026-11-10 01:00 EST. Values are whole
percentages as the app reports them, so a change of "1 point" means anywhere from about 0.1 to 1.9.

| Time | Phase | Moment | 5-hour % | Weekly % | Context tokens | Context reset before this |
|---|---|---|---|---|---|---|
| 2026-11-08T00:00:55-05:00 | planning | session start | not read | not read | | new session |
| 2026-11-08T00:20-05:00 | planning | during review turn | 12 | 50 | 127,976 | none |
| 2026-11-08T00:28-05:00 | 0 | phase start | 15 | 51 | 157,199 | none |
| 2026-11-08T00:43:25-05:00 | 0 | phase end | 25 | 52 | 268,883 | none |
| 2026-11-08T00:51:29-05:00 | 0 | just before first /compact | 28 | 53 | 293,955 | none (next row is after /compact) |
| 2026-11-08T00:57:55-05:00 | 1 | after first /compact (phase start) | 31 | 53 | 81,551 | /compact by Marcus at 00:57:16 (manual; 305,065 tokens before, 14,969 after, 56.5 s) |
| 2026-11-08T01:13-05:00 | 1 | before turning off Claude Docs connector | 36 | 54 | 137,955 | none (MCP tools 20,442; MCP instructions 2,339) |
| 2026-11-08T01:21-05:00 | 1 | after turning off Claude Docs connector | 37 | 54 | 146,790 | none (MCP tools 20,906; MCP instructions 1,700) |
| 2026-11-08T01:30-05:00 | 1 | Claude checks done, waiting for Marcus checklist | 42 | 54 | 198,396 | none |
| 2026-11-11T09:46:57-05:00 | 1 | after a 3-day pause (weekly limit reset Nov 10) | 4 | 8 | 207,766 | none (same session resumed) |
| 2026-11-11T09:52-05:00 | 1 | Phase 1 closed | 5 | 8 | 224,386 | none |
| 2026-11-11T09:54:22-05:00 | 1 | before the sample redesign | 8 | 8 | 237,728 | none |
| 2026-11-11T09:59:10-05:00 | 1 | just before /clear | 9 | 9 | 248,054 | none (next row is after /clear) |
| 2026-11-11T10:00:44-05:00 | 2 | after /clear (phase start) | 10 | 9 | 78,618 | /clear by Marcus (manual; 248,054 tokens before) |
| 2026-11-11T10:21:20-05:00 | 2 | checks built, just before /compact | 22 | 10 | 198,481 | none (next row is after /compact) |
| 2026-11-11T10:31:23-05:00 | 2 | after /compact (pilot start) | 24 | 11 | 89,035 | /compact by Marcus (manual; 198,481 tokens at the last reading before it) |
| 2026-11-11T10:43:12-05:00 | 2 | pilot 3 of 5 done, just before /compact | 34 | 12 | 218,345 | none (next row is after /compact) |
| 2026-11-11T10:47:46-05:00 | 2 | after /compact (pilot school 4 next) | 37 | 12 | 99,537 | /compact by Marcus (manual; 218,345 tokens at the last reading before it); includes one short question turn about published prompts |
| 2026-11-11T10:55:09-05:00 | 2 | pilot done (5 of 5) and codebook v2, just before /compact | 43 | 13 | 172,762 | none (next row is after /compact) |
| 2026-11-11T10:59:34-05:00 | 2 | after /compact (main coding, 10 schools next) | 45 | 13 | 88,911 | /compact by Marcus (manual; 172,762 tokens at the last reading before it) |
| 2026-11-11T11:06:11-05:00 | 2 | main coding 3 of 10 (8 of 15 coded), just before /compact | 49 | 14 | 165,412 | none (next row is after /compact) |
| 2026-11-11T11:08:58-05:00 | 2 | after /compact (main coding, 7 schools next) | 52 | 14 | 89,371 | /compact by Marcus (manual; 165,412 tokens at the last reading before it) |
| 2026-11-11T11:14:27-05:00 | 2 | main coding 6 of 10 (11 of 15 coded), just before /compact | 57 | 15 | 170,108 | none (next row is after /compact) |
| 2026-11-11T11:16:38-05:00 | 2 | after /compact (main coding, 4 schools next) | 59 | 15 | 93,176 | /compact by Marcus (manual; 170,108 tokens at the last reading before it) |
| 2026-11-11T11:24:12-05:00 | 2 | main coding done (15 of 15 coded and passing), just before /compact | 66 | 16 | 195,190 | none (next row is after /compact) |
| 2026-11-11T11:28:24-05:00 | 2 | after /compact (Phase 2 wrap-up next) | 69 | 17 | 86,616 | /compact by Marcus (manual; 195,190 tokens at the last reading before it) |
| 2026-11-11T11:33:07-05:00 | 2 | phase end, just before /compact | 71 | 17 | 118,314 | none (next row is after /compact) |
| 2026-11-11T11:58:16-05:00 | 3 | after /compact (phase start) | 74 | 17 | 84,625 | /compact by Marcus (manual; 118,314 tokens at the last reading before it) |
| 2026-11-11T12:11:53-05:00 | 3 | tabs built (a /compact was prepared here, then put off until Marcus finished the checklist) | 86 | 19 | 210,753 | none |
| 2026-11-11T12:22:58-05:00 | 3 | phase end, just before /compact | 87 | 19 | 219,395 | none (next row is after /compact) |
| 2026-11-11T12:27:10-05:00 | 4 | after /compact (phase start) | 89 | 19 | 90,315 | /compact by Marcus (manual; 219,395 tokens at the last reading before it) |
| 2026-11-11T14:47:36-05:00 | 4 | after /compact (taken late: about 25k tokens of work ran first; no reading was taken just before this /compact, when the 5-hour window had run out) | 3 | 21 | 111,661 | /compact by Marcus at 12:45 (manual; the transcript records 209,907 tokens before it, after a stopped tool call) |
| 2026-11-11T14:53:40-05:00 | 4 | build done and live; Marcus's checklist next | 7 | 21 | 149,989 | none |
| 2026-11-11T15:02:53-05:00 | 4 | phase end, just before /compact | 8 | 22 | 157,588 | none (next row is after /compact) |
| 2026-11-11T15:06:20-05:00 | 5 | after /compact (Phase 5 start) | 10 | 22 | 80,741 | /compact by Marcus at 15:05:24 (manual, phase end; the transcript records 161,915 tokens before it) |
| 2026-11-11T15:24:14-05:00 | 5 | 2 of 21 new schools coded, just before /compact | 19 | 23 | 211,489 | none (next row is after /compact) |
| 2026-11-11T15:27:12-05:00 | 5 | after /compact (2 of 21 coded) | 22 | 24 | 96,807 | /compact by Marcus (manual, big chunk; 211,489 tokens before it) |
| 2026-11-11T15:36:21-05:00 | 5 | 5 of 21 new schools coded, just before /compact | 29 | 24 | 190,298 | none (next row is after /compact) |
| 2026-11-11T15:38:46-05:00 | 5 | after /compact (5 of 21 coded) | 32 | 25 | 100,588 | /compact by Marcus (manual, big chunk; 190,298 tokens before it) |
| 2026-11-11T15:48:09-05:00 | 5 | 7 of 21 new schools coded, just before /compact | 39 | 26 | 188,198 | none (next row is after /compact) |
| 2026-11-11T15:50:01-05:00 | 5 | after /compact (7 of 21 coded) | 42 | 26 | 99,527 | /compact by Marcus (manual, big chunk; 188,198 tokens before it) |
| 2026-11-11T15:56:15-05:00 | 5 | 9 of 21 new schools coded, just before /compact | 46 | 27 | 167,067 | none (next row is after /compact) |
| 2026-11-11T16:00:35-05:00 | 5 | after /compact (9 of 21 coded) | 48 | 27 | 98,504 | /compact by Marcus (manual, big chunk; 167,067 tokens before it) |
| 2026-11-11T16:08:37-05:00 | 5 | 11 of 21 new schools coded, just before /compact | 55 | 28 | 187,119 | none (next row is after /compact) |
| 2026-11-11T16:13:23-05:00 | 5 | after /compact (11 of 21 coded) | 57 | 28 | 99,718 | /compact by Marcus (manual, big chunk; 187,119 tokens before it) |

## Cost per phase
| Phase | 5-hour points | Weekly points | Context growth (tokens) |
|---|---|---|---|
| planning, 00:20 to 00:28 only | 3 | 1 | 29,223 |
| 0 Foundation | 10 | 1 | 111,684 |

The first 20 minutes of planning were not measured: no reading was taken at session start.

Between 00:51:29 and 00:57:55 the 5-hour window moved 3 points. That covers one short turn (recording a decision) plus the compaction itself, and they cannot be separated: the transcript keeps no record of the compaction's own model call (`evidence/phase1-recon/`). The context the next turn re-reads fell from 293,955 to 81,551 tokens, of which about 78,000 is fixed overhead (tool definitions, system prompt, skills) sent on every turn.

Connector test (01:13 to 01:21): turning off the Claude Docs connector saved about 175 tokens per turn, not the thousands Claude predicted. MCP tool descriptions went up 464 (a Workflow tool appeared at the same time) and MCP instructions went down 639. The 20,000 tokens of MCP tools are almost all built into the app (browser, computer control, app controls), which cannot be switched off from a session.
