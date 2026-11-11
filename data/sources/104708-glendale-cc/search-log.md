# Search log: Glendale Community College (104708), domain gccaz.edu

Searched 2026-11-11 from 15:33 EST with Claude's WebSearch tool (standard mode). Phase 5, round 2,
codebook v2. The four fixed searches returned no gccaz.edu pages at all (results were Glendale
Community College in California at glendale.edu, Greenfield CC at gcc.mass.edu, Georgia College,
Grand Rapids CC and others; all skipped), so three extra searches were run with `allowed_domains`.
Glendale Community College is one of the Maricopa County Community Colleges; the district's
Administrative Regulations bind all its colleges, and the college's own syllabus page points to
"Student Handbook, section 2.3.11, Academic Misconduct", which is district regulation 2.3.11.

Fetching: www.gccaz.edu, district.maricopa.edu, www.maricopa.edu and mcli.maricopa.edu all answer
curl with HTTP 403 (a bot check). The raw 403 copies are saved as a record
(2026-11-11-syllabus-elements.html, 2026-11-11-district-ar-2-3.html,
2026-11-11-maricopa-student-ai-tools.html, 2026-11-11-mcli-syllabus-statements.html,
2026-11-11-cs-program.html). Pages behind values were read in Claude's browser pane instead. The
district regulation page is 82,842 characters of text; only its section 2.3.11 (from that heading up
to the 2.3.12 heading) was copied from the pane and saved with `--rendered` as
2026-11-11-district-ar-2-3.rendered.txt. The browser pane also showed that the CS program page and
the syllabus common elements page contain no text on AI.

## Search: gccaz.edu generative AI policy
- no gccaz.edu results (glendale.edu is Glendale Community College in California, a different college; skipped)

## Search: gccaz.edu computer science AI policy
- no gccaz.edu results

## Search: gccaz.edu software engineering syllabus AI
- https://gccaz.edu/academics/syllabus-elements (Syllabus Common Elements, policies that are part of every GCC syllabus; curl 403; read in the browser pane: no text on AI; refers to Student Handbook section 2.3.11 for academic misconduct)
- no software engineering syllabus in the results

## Search: gccaz.edu ChatGPT academic integrity
- no gccaz.edu results

## Search: gccaz.edu artificial intelligence course policy
- https://www.gccaz.edu/degrees-certificates/artificial-intelligence (AI degree program built with Intel; a program, not a use rule; not opened)
- the rest were other colleges (glendale.edu, cgc.edu, Austin CC, Pima, CSUN, University of Arizona and others); skipped
- no relevant results for the department

## Search: gccaz.edu AI syllabus statement
- https://gccaz.edu/academics/syllabus-elements (see above; no text on AI)
- the rest were other colleges' sample statements; skipped
- no relevant results for the department
- From the maricopa.edu search below: https://mcli.maricopa.edu/resources/artificial-intelligence/syllabus-statements-regarding-generative-artificial-intelligence (district model syllabus statements for faculty: no AI, some AI, AI allowed; curl 403; saved as a record; example language for instructors, not a rule; not read)

## Extra search: Glendale Community College artificial intelligence AI students academic integrity syllabus (allowed_domains gccaz.edu)
- https://www.gccaz.edu/academics/syllabus-elements (see above)
- https://guides.gccaz.edu/ai-chat/notes (library AI Chat Workshops guide, Important Notes; opened; saved as 2026-11-11-library-ai-chat-notes.html; the page coded for collaboration)
- 2022-23, 2023-24 and 2024-25 academic catalogs (PDF); the 2024-25 catalog was opened and saved as 2026-11-11-catalog-2024-25.pdf; no text on AI use (AI appears only as a degree program)
- AI, information technology and cybersecurity program pages; not opened

## Extra search: Glendale Community College computer science CSC course software (allowed_domains gccaz.edu)
- https://www.gccaz.edu/degrees-certificates/computer-science (Computer Science program overview; curl 403, saved as a record; read in the browser pane: 526 characters, no text on AI)
- https://www.gccaz.edu/degrees-certificates/computer-and-information-technology/associate-science-emphasis-computer-science-8601-as (A.S., emphasis in Computer Science: CSC110, CSC205, CSC230, CSC240; no software engineering course; not opened)
- Programming and Systems Analysis and CIS program pages; not opened
- No software engineering course or syllabus was found.

## Extra search: Maricopa Community Colleges generative AI student policy academic misconduct (allowed_domains maricopa.edu)
- https://district.maricopa.edu/regulations/admin-regs/section-2/2-3 (Administrative Regulation 2.3 Scholastic Standards, section 2.3.11 Academic Misconduct, amended April 7, 2026; curl 403; read in the browser pane; section saved as 2026-11-11-district-ar-2-3.rendered.txt; the page coded for the university)
- https://www.maricopa.edu/students/artificial-intelligence-ai/tools (district student page on AI tools; curl 403; saved as a record; not read)
- https://mcli.maricopa.edu/resources/artificial-intelligence/guidance-maricopa-faculty-regarding-generative-ai-tools-and-academic-misconduct (faculty guidance on detectors; not opened)
- AI Task Force executive summary and data security guidelines; not opened
