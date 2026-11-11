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
