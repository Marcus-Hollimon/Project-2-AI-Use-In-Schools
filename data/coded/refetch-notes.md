## Follow-up checks

Some sites answer curl with HTTP 403 on some requests and HTTP 200 on others. Refused pages were
not retried with other headers (project rule). Runs on 2026-11-11:

- First run (11:28): 4 pages refused with HTTP 403: the Johns Hopkins teaching guidelines and
  syllabus-statements pages, the Valparaiso 2010 CS 358 syllabus, and the Virginia CS undergraduate
  page. Only the Johns Hopkins guidelines page carries coded quotes (univ_stance, univ_tone,
  disclosure). At 11:30:29 it was opened in Claude's browser pane: it loads ("Last update 2/19/26")
  and all 3 coded quotes are on it word for word.
- Second run (11:31): both Johns Hopkins pages answered HTTP 200, and the script found all 3 coded
  quotes in the new copy itself. Valparaiso and Virginia still refused; neither carries a coded quote.

So a "refused" row means the site blocked that request, not that the page was removed.

- Third run (Phase 5, all 36 schools, 184 pages; finished before 2026-11-11T19:48:36-05:00): 109 unchanged, 57 changed,
  12 refused, 4 gone, 2 rendered text. No coded quote is missing from any changed page. The 4 gone
  pages (3 Iowa State, 1 Stanford) already answered HTTP 404 when they were first saved and no coded
  value uses them; they are kept as evidence of what the search returned. Of the 12 refused pages,
  two carry coded quotes. The Johns Hopkins guidelines page was opened again in the browser pane
  shortly before this note was written (2026-11-11T19:48:36-05:00): it loads ("Last update 2/19/26") and all 3 coded quotes are on it word for word. The
  Tidewater code PDF (2 quotes; HTTP 200 when saved at 16:55 the same day) was not opened, because a
  PDF in the browser pane becomes a download, which needs Marcus's permission.
