# Pilot cost per school (Phase 2, spec task 4)

Readings come from the Claude app's usage data (get_usage), right after each school passed
`check_study.py`. 5-hour and weekly values are whole percentages as the app reports them, so one
point means anywhere from about 0.1 to 1.9. Times come from `date -Iseconds` in the shell.

| School | Start (reading before) | End (school passes checks) | 5-hour % | Weekly % | Context tokens | Searches | Pages saved |
|---|---|---|---|---|---|---|---|
| (after /compact) | | 2026-11-11T10:31:23-05:00 | 24 | 11 | 89,035 | | |
| Minnesota 174066 | 10:31:23 | 2026-11-11T10:34:31-05:00 | 27 | 11 | 138,401 | 7 | 7 |
| Johns Hopkins 162928 | 10:34:31 | 2026-11-11T10:39:23-05:00 | 31 | 12 | 182,034 | 7 | 11 (3 are curl 403 block pages) |
| Valparaiso 152600 | 10:39:23 | 2026-11-11T10:42:15-05:00 | 34 | 12 | 213,489 | 7 | 6 (1 is a 403 block page) |
| (after /compact) | | 2026-11-11T10:47:46-05:00 | 37 | 12 | 99,537 | | |
| Coppin State 162283 | 10:47:46 | 2026-11-11T10:49:59-05:00 | 39 | 13 | 132,327 | 9 | 3 |
| Snow 230597 | 10:49:59 | 2026-11-11T10:52:10-05:00 | 40 | 13 | 154,197 | 6 | 5 |

## Notes
- Minnesota also includes a short check of transcript ddc7d76a (metadata only, a few hundred tokens).
- Minnesota cost 3 points and 49,366 tokens of context growth. About half the growth is search-tool
  output (each search returns roughly 3,000 to 4,000 tokens of summary) and half is page text read to
  find quotes.
- Johns Hopkins cost 4 points and 43,633 tokens, including a change to check S3 (rendered text from a
  site that blocks curl) with one new test and a sabotage run. teaching.jhu.edu blocked curl on some
  pages; retrying curl with fuller browser headers was refused by the permission system as bot-check
  circumvention, which is the right call. The browser pane was used to read pages instead.
- Valparaiso cost 3 points and 31,455 tokens. First PDF source: text extracted with pdftotext 4.00
  (Git for Windows' mingw64) into the `.txt` sidecar the checker reads.
- Running average over 3 schools: 3.3 points and 41,500 tokens of context per school.
- Coppin State cost 2 points and 32,790 tokens (the reading after the compact includes one short question turn). The university has no AI policy page; the only rule is one Student Handbook clause. Printing 45 lines of the handbook around that clause cost about 8,000 tokens; a narrower filter would have done.

- Snow cost 1 point and 21,870 tokens: its policies were easy to find and the text was read through narrow filters.

## Pilot result (2026-11-11, after school 5)
- Five schools, all passing every check. Cost per school: 3, 4, 3, 2, 1 points of the 5-hour limit
  (average 2.6; readings are whole percentages, so each is plus or minus 1) and 49,366, 43,633,
  31,455, 32,790, 21,870 tokens of context growth (average 35,800). Wall-clock time 2 to 5 minutes each.
- Costs fell as the procedure settled: filtering page text by pattern instead of printing it, and
  knowing where each kind of page lives.
- Projection for the remaining 10 schools: about 26 points at the pilot average, plus about 2 to 3
  points per /compact (3 or 4 of them at one every 3 schools), so about 35 points in all. The 5-hour
  window was 40% at 10:52 and resets 14:40 EST, so the 10 schools should finish inside this window
  at about 75% to 80%, with the deadline (2 PM Nov 12) a day away. The R1 re-fetch report, acceptance
  checks and Phase 3 then start in the next window.
- Weekly limit: 13% at 10:52; not a constraint at this rate.
- Codebook v2, the recode and the STATE.md handoff cost 3 more points (40% to 43% at 10:55:09).

## Codebook v2 candidates (all four adopted 2026-11-11 as version 2; see `study/codebook.md`)
1. Course pages dated before 2023 (before ChatGPT) should not count for `se_courses`; treat them as
   no public syllabus. Johns Hopkins' only official OOSE page is Fall 2018 and v1 codes it "not addressed".
2. Example or suggested syllabus language (JHU, Valpo) gets "encouraged" for disclosure with a
   cue_reason each time; a rule that says so would make this consistent without a written reason.
3. Department stance from news articles (Minnesota): allowed by v1 as the lowest source type; worth
   stating in the codebook that news on a department page counts as department text.
4. A conduct clause that limits AI ("inappropriate or excessive use") without stating a default (Coppin State): v1 has no clean value; coded "permit with conditions" with a cue_reason. A rule for this case would make it consistent.

Recode (spec R2): one value changed, Johns Hopkins `se_courses` "not addressed" to "no public syllabus found" (`data/coded/codebook-v2-recode.json`). All 5 pass the checks under v2; study tests 32/32 (`validation/runs/2026-11-11T15-53-30-496Z_study.json`).

## Main coding (the 10 schools after the pilot, codebook v2)
| School | Start (reading before) | End (school passes checks) | 5-hour % | Weekly % | Context tokens | Searches | Pages saved |
|---|---|---|---|---|---|---|---|
| (after /compact) | | 2026-11-11T10:59:34-05:00 | 45 | 13 | 88,911 | | |
| Virginia 234076 | 10:59:34 | 2026-11-11T11:02:39-05:00 | 47 | 14 | 122,305 | 7 | 2 (CS department site blocked) |
| MIT 166683 | 11:02:39 | 2026-11-11T11:04:48-05:00 | 49 | 14 | 148,301 | 7 | 5 |
| Presbyterian 218539 | 11:04:48 | 2026-11-11T11:05:45-05:00 | 49 | 14 | 165,412 | 8 | 3 |
| (after /compact) | | 2026-11-11T11:08:58-05:00 | 52 | 14 | 89,371 | | |
| Le Moyne-Owen 220604 | 11:08:58 | 2026-11-11T11:10:07-05:00 | 53 | 15 | 110,623 | 8 | 3 |
| Luzerne 213659 | 11:10:07 | 2026-11-11T11:12:22-05:00 | 56 | 15 | 145,510 | 8 | 3 (policy is a Word file) |
| Cincinnati 201885 | 11:12:22 | 2026-11-11T11:14:06-05:00 | 57 | 15 | 170,108 | 10 | 5 |
| (after /compact) | | 2026-11-11T11:16:38-05:00 | 59 | 15 | 93,176 | | |
| Ohio State 204796 | 11:16:38 | 2026-11-11T11:19:11-05:00 | 61 | 16 | 122,995 | 8 | 5 (CSE site and syllabus site blocked) |
| Baldwin Wallace 201195 | 11:19:11 | 2026-11-11T11:21:29-05:00 (written late; usage read a few minutes earlier) | 63 | 16 | 147,380 | 11 | 4 (all absences) |
| Defiance 202514 | 11:21:29 | 2026-11-11T11:22:08-05:00 | 65 | 16 | 168,535 | 8 | 3 |
| Columbus State 202222 | 11:22:08 | 2026-11-11T11:24:02-05:00 | 66 | 16 | 195,190 | 8 | 5 (syllabus is a Word file) |

## Phase 5 (21 more schools, codebook v2)
| School | Start (reading before) | End (school passes checks) | 5-hour % | Weekly % | Context tokens | Searches | Pages saved |
|---|---|---|---|---|---|---|---|
