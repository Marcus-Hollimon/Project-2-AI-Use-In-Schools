# R1 re-fetch report

Generated 2026-11-11T11:32:06-05:00 by `study/refetch.py`. Every archived source URL was fetched again with the same curl command used to save it. A report, not a failure: policies change.

| Result | Pages |
|---|---|
| changed | 26 |
| refused | 2 |
| unchanged | 41 |

Coded quotes no longer found in the new copy of a changed page: 0.

## Changed

| Archive | Coded quotes | Detail |
|---|---|---|
| `data/sources/162928-johns-hopkins/2026-11-11-cs-home.html` | 0 | no quotes coded from this page |
| `data/sources/162928-johns-hopkins/2026-11-11-cs-integrity-code.html` | 0 | no quotes coded from this page |
| `data/sources/162928-johns-hopkins/2026-11-11-cs-support-ai-wiki.html` | 0 | no quotes coded from this page |
| `data/sources/162928-johns-hopkins/2026-11-11-teaching-genai-guidelines.html` | 3 | all 3 still present |
| `data/sources/162928-johns-hopkins/2026-11-11-teaching-genai-main.html` | 0 | no quotes coded from this page |
| `data/sources/162928-johns-hopkins/2026-11-11-teaching-genai-policy.html` | 0 | no quotes coded from this page |
| `data/sources/162928-johns-hopkins/2026-11-11-teaching-genai-syllabus.html` | 0 | no quotes coded from this page |
| `data/sources/166683-mit/2026-11-11-eecs-undergrad.html` | 0 | no quotes coded from this page |
| `data/sources/174066-minnesota/2026-11-11-cs-academic-conduct.html` | 0 | no quotes coded from this page |
| `data/sources/174066-minnesota/2026-11-11-cs-home.html` | 0 | no quotes coded from this page |
| `data/sources/174066-minnesota/2026-11-11-cse-news-ai-literacy.html` | 0 | no quotes coded from this page |
| `data/sources/174066-minnesota/2026-11-11-cse-news-ai-workplace.html` | 3 | all 3 still present |
| `data/sources/174066-minnesota/2026-11-11-provost-ai-in-classes.html` | 0 | no quotes coded from this page |
| `data/sources/174066-minnesota/2026-11-11-provost-genai-syllabus.html` | 3 | all 3 still present |
| `data/sources/201195-baldwin-wallace/2026-11-11-cs-major.html` | 0 | no quotes coded from this page |
| `data/sources/201195-baldwin-wallace/2026-11-11-csc310-catalog.html` | 0 | no quotes coded from this page |
| `data/sources/201195-baldwin-wallace/2026-11-11-se-major.html` | 0 | no quotes coded from this page |
| `data/sources/201885-cincinnati/2026-11-11-ai-guidelines.html` | 2 | all 2 still present |
| `data/sources/201885-cincinnati/2026-11-11-ai-students.html` | 0 | no quotes coded from this page |
| `data/sources/201885-cincinnati/2026-11-11-ai-teaching-rftl.html` | 0 | no quotes coded from this page |
| `data/sources/201885-cincinnati/2026-11-11-chatgpt-guide-blog.html` | 1 | all 1 still present |
| `data/sources/201885-cincinnati/2026-11-11-cs-department.html` | 0 | no quotes coded from this page |
| `data/sources/213659-luzerne/2026-11-11-cs-program.html` | 0 | no quotes coded from this page |
| `data/sources/213659-luzerne/2026-11-11-student-forms.html` | 0 | no quotes coded from this page |
| `data/sources/218539-presbyterian/2026-11-11-cs-program.html` | 0 | no quotes coded from this page |
| `data/sources/220604-le-moyne-owen/2026-11-11-cs-program.html` | 0 | no quotes coded from this page |

## Refused

| Archive | Coded quotes | Detail |
|---|---|---|
| `data/sources/152600-valparaiso/2026-11-11-cs358-syllabus-spring2010.html` | 0 | HTTP 403 (site refused the request; the page may still exist) |
| `data/sources/234076-virginia/2026-11-11-cs-undergrad.html` | 0 | HTTP 403 (site refused the request; the page may still exist) |

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
