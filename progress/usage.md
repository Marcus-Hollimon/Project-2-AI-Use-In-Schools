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

## Cost per phase
| Phase | 5-hour points | Weekly points | Context growth (tokens) |
|---|---|---|---|
| planning, 00:20 to 00:28 only | 3 | 1 | 29,223 |
| 0 Foundation | 10 | 1 | 111,684 |

The first 20 minutes of planning were not measured: no reading was taken at session start.
