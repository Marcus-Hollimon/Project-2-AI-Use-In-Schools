# Pilot cost per school (Phase 2, spec task 4)

Readings come from the Claude app's usage data (get_usage), right after each school passed
`check_study.py`. 5-hour and weekly values are whole percentages as the app reports them, so one
point means anywhere from about 0.1 to 1.9. Times come from `date -Iseconds` in the shell.

| School | Start (reading before) | End (school passes checks) | 5-hour % | Weekly % | Context tokens | Searches | Pages saved |
|---|---|---|---|---|---|---|---|
| (after /compact) | | 2026-11-11T10:31:23-05:00 | 24 | 11 | 89,035 | | |
| Minnesota 174066 | 10:31:23 | 2026-11-11T10:34:31-05:00 | 27 | 11 | 138,401 | 7 | 7 |
| Johns Hopkins 162928 | 10:34:31 | 2026-11-11T10:39:23-05:00 | 31 | 12 | 182,034 | 7 | 11 (3 are curl 403 block pages) |

## Notes
- Minnesota also includes a short check of transcript ddc7d76a (metadata only, a few hundred tokens).
- Minnesota cost 3 points and 49,366 tokens of context growth. About half the growth is search-tool
  output (each search returns roughly 3,000 to 4,000 tokens of summary) and half is page text read to
  find quotes.
- Johns Hopkins cost 4 points and 43,633 tokens, including a change to check S3 (rendered text from a
  site that blocks curl) with one new test and a sabotage run. teaching.jhu.edu blocked curl on some
  pages; retrying curl with fuller browser headers was refused by the permission system as bot-check
  circumvention, which is the right call. The browser pane was used to read pages instead.
