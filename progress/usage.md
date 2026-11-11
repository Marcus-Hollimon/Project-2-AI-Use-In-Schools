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

## Cost per phase
| Phase | 5-hour points | Weekly points | Context growth (tokens) |
|---|---|---|---|
| planning, 00:20 to 00:28 only | 3 | 1 | 29,223 |
| 0 Foundation | 10 | 1 | 111,684 |

The first 20 minutes of planning were not measured: no reading was taken at session start.

Between 00:51:29 and 00:57:55 the 5-hour window moved 3 points. That covers one short turn (recording a decision) plus the compaction itself, and they cannot be separated: the transcript keeps no record of the compaction's own model call (`evidence/phase1-recon/`). The context the next turn re-reads fell from 293,955 to 81,551 tokens, of which about 78,000 is fixed overhead (tool definitions, system prompt, skills) sent on every turn.

Connector test (01:13 to 01:21): turning off the Claude Docs connector saved about 175 tokens per turn, not the thousands Claude predicted. MCP tool descriptions went up 464 (a Workflow tool appeared at the same time) and MCP instructions went down 639. The 20,000 tokens of MCP tools are almost all built into the app (browser, computer control, app controls), which cannot be switched off from a session.
