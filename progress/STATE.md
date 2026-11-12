# State: read this first

Current phase: 5 More schools (15 to 36; spec `specs/phase-5-more-schools.md`, approved by Marcus 15:15:40 with one extra Ohio school, so 21 new, 36 in all). Evaluation moves to Phase 6. Phase 4 Validation is done.

Last updated: 2026-11-11T16:59:31-05:00 by Claude (session a9056776). ALL 21 new schools coded; full checker
36 PASS, 0 FAIL; study tests 40/40 recorded (validation/runs/2026-11-11T21-59-21-021Z_study.json). Marcus chose
to push past the 85% stop line at 16:53 (progress/decisions.md); the 5-hour window was 90% at 16:59 (resets
7:40 PM EST). Coding is DONE.
Update 2026-11-11T17:18:05-05:00: site update mostly done (commit 0e9db80): Research tab has a "What the data
shows" list (4 sentences, web/src/data.js findings(), claims research-finding-*); web tests 49/49 recorded
(22-17-33Z) after a recorded mutation run that failed as it should (22-17-20Z); stale "15" fixed. build.py
rebuilt data/derived and exits 1 ONLY on C3_compact (C5 now passes). STOPPED at 95% of the 5-hour window.
Update 2026-11-11T19:53:03-05:00 (after Marcus's /compact and the 7:40 PM reset): (a) Research tab checked in the
browser pane (the project2-web entry in C:\Claude Folder\.claude\launch.json): 36 schools, 0 failing, 7 tables, no console errors, no sideways
scroll at 375 px. (b) R1 re-fetch rerun: 184 pages, 0 coded quotes missing (refetch-notes.md). (c) Pipeline
19/19 recorded after two recorded mutation runs. (d) C2 had begun failing on an app placeholder reply
(model <synthetic>): fixed as a counting bug. C3 was failing on TWO compacts (15:59, 16:12), not one; all 3
over-count compacts followed a reply with a thinking block; Marcus chose "Allow, list the gap" (decisions.md,
phase-1 spec amendment). build.py now exits 0, all checks PASS. (f) Acceptance boxes ticked except deploy.
Pushed 01a3e56; deploy run 43130741613 succeeded; live site checked 2026-11-11T19:55:17-05:00; all six acceptance boxes ticked.
Update 2026-11-11T20:20:01-05:00: Marcus's checklist passed; judgment calls decided.
Update 2026-11-11T20:34:55-05:00: ALL judgment-call decisions APPLIED as codebook v3 (plus a 12th call, rule-list tone = neutral,
decided after the /compact). 23 values changed at 16 schools; all 37 tone values re-read; before/after and the basis
for every tone value in data/coded/codebook-v3-recode.json. check_study 36/36 PASS; study 42/42, web 49/49,
pipeline 19/19 recorded, with mutation runs for the new C2 rule and the disclosure split; build exit 0; browser
checked. NEXT: commit, push, deploy check, then report every moved number to Marcus. After that: Phase 6
(evaluation) needs its spec written and approved first.
Minor, not fixed: 10 of the original 15 schools have no coded_at field (all were coded 2026-11-11 per git).

## DONE: Marcus's judgment-call decisions, applied as codebook v3 (the plan as it was written)
Marcus ran his Phase 5 checklist: all 4 passed (spec ticked). Then he decided 11 judgment calls. Everything
below was applied on 2026-11-11 evening (see the update line at the top).

Recodes in `data/coded/values.json` (write a scratchpad script; record every before/after in a new
`data/coded/codebook-v3-recode.json`, like `codebook-v2-recode.json`):
1. Penn se_courses -> "no public syllabus found" (CIS 3500 Software Design/Engineering is the named course; its
   catalog description in 2026-11-11-catalog-cis-courses.html has no AI text; CIS 2500 goes in the note).
2. Case Western se_courses -> "no public syllabus found" (CSDS 393 Software Engineering has nothing public;
   CSDS 293 statement goes in the note).
3. UDC: univ_stance -> "none found", collaboration -> "not discussed", disclosure -> "not stated" (library's own
   words no longer count). univ_tone stays positive (president's AI Initiative page) WITH a new field
   `stance_tone_reason`; change check C2 in study/check_study.py to accept stance "none found" + a tone only
   when the tone entry has stance_tone_reason; add a study test. UDC se_courses unchanged.
4. Defiance: univ_stance -> "none found", univ_tone -> "none found", disclosure -> "not stated" (all came from
   library.defiance.edu). Check its search log has the second searches (N1) for none found.
5. Tidewater: univ_stance stays restrict, re-sourced to the CURRENT Policy 2214 Rev 1 (Jan 26 2026), archive
   data/sources/233772-tidewater/2026-11-11-policy-2214-student-code-of-conduct-2026.pdf (saved with
   save_page.py, HTTP 200; text .txt beside it), quote "This may include unauthorized use of AI tools." (4.25),
   source_type policy page. disclosure -> "not stated" (Marcus). collaboration -> "not discussed".
   univ_tone re-read from official text only (the policy is procedural: likely neutral).
   The Rev 0 (July 2025) copy downloaded through the browser with Marcus's permission is kept as evidence
   (2026-11-11-policy-2214-student-code-of-conduct.pdf, meta kind "raw bytes from Claude's browser pane").
   The college's official policies page (tcc.edu/about-tcc/statements-policies/college-policies/) links only
   the Rev 1 file and says those are the only official college-wide policies. Update the search log.
6. Maine Fort Kent collaboration -> "not discussed" (the brainstorming line was a sample statement borrowed from
   another school on a library page; the official AIatUMFK guidance page has no collaboration text).
7. Berry: values stay, but re-source univ_tone (neutral), collaboration (in passing: "You can choose to use
   generative AI tools to help brainstorm assignments...") and disclosure (encouraged, example wording: "students
   must cite any AI-generated material that informed their work", cue_reason: example language, codebook v2
   rule 2) to the official "Berry Syllabus Statement on AI" in 2026-11-11-libguide-faculty-considerations.html.
8. Tone: codebook v3 adds "mixed" (opportunities and risks both get real weight; neither dominates). Re-read
   EVERY univ_tone and dept_tone that is not "none found" (about 30 + 4) from its archived page and recode to
   positive / neutral / cautionary / mixed, with a short note of the basis. The 4 already flagged as balanced:
   Maine Fort Kent, Tidewater, Nova Southeastern, Temple. Tone has no cue words (null), so C3 is unaffected.

Codebook v3 (`study/codebook.json` version 3 + `study/codebook.md` "Changes in version 3"; a test checks they
agree): add tone value "mixed"; write the rules Marcus chose: (a) se_courses: code the course NAMED Software
Engineering first, the nearest equivalent only when none is named so, never switch to another course because it
has text; (b) a catalog description counts as a course page only when it says the course teaches or uses AI;
(c) a university library's AI guide counts as university text only where it reproduces official university
text or is itself the official guidance (as at UMFK); (d) disclosure read from a plagiarism or cheating rule
that names missing credit is allowed and is counted separately on the site; (e) stance "none found" with a tone
needs stance_tone_reason. Nevada State stays (school page stands in for the missing department; write it down).
Checker changes S3 (empty 202) and campus subdomains: approved by Marcus, note in the spec.

Site: the disclosure finding sentence must show the split: how many "required" were stated outright and how many
were read from a plagiarism or cheating rule (cue_reason present). Update web/src/data.js findings(), its test in
web/src/tabs.test.jsx (count independently from values.json), and claims.json if needed. Then: full check_study,
study tests (+ a mutation run for the new C2 rule), web tests (+ mutation run for the split), pipeline tests,
build.py exit 0, browser check, push, deploy check, and a summary for Marcus of every number that moved.
Expected moves: syllabus finding 24/30 national (Penn), 5/6 Ohio (Case Western); stance national none found
2->3 (UDC), instructor decides 10->9; Ohio restrict 4->3, none found 1->2 (Defiance); disclosure required
national 12->10 (UDC, Tidewater), Ohio 3->2 (Defiance). Recount from the data after recoding; do not trust these.

## Earlier notes (all done; kept for the record)
1. Take a usage reading marked "after /compact" (full 7-column row in `progress/usage.md`, phase 5).
2. Coding is finished: all 36 schools pass. Next is the rest of the Phase 5 spec: the site's "What the data
   shows" claims and their tests, a web mutation run, texts that still say "15", the R1 re-fetch, recorded
   study/web/pipeline runs, C3_compact with Marcus (build must exit 0), push, deploy check, spec checkboxes, and
   Marcus's checklist with every judgment call below. Watch the 5-hour window: at 100% all work stops.
   Done and passing: Berry, Tidewater, Case Western, Iowa State,
   Stanford, NYIT, West Virginia Wesleyan, Glendale CC, Arizona State, Rice, Eastern Kentucky, Nevada State,
   UDC, UMKC, Penn, College of Charleston, Westminster, Niagara CC, Temple, Nova Southeastern, Maine Fort Kent (rows in `progress/pilot-cost.md`).
   About 2 to 6 five-hour points and 30k to 50k context per school (Maine Fort Kent cost 4).
   Only 2 schools fit between compacts at that rate (context starts near 100k after a compact). Cost rows: scratchpad `costrow.py "<School unitid>" <start> <5h> <weekly>
   <context> <searches> "<pages>"` (takes the time from `date -Iseconds` itself).
3. Prepare the next /compact after about 3 to 4 more schools (context near 190k).
4. Judgment calls to list for Marcus at the end: West Virginia Wesleyan univ_stance restrict (the 2025-26
   handbook and May 2026 tech FAQ give a no-use default; the July 2026 AI policy leaves it to instructors);
   Glendale CC coded from Maricopa district regulation 2.3.11 (domain_reason), the first value saved as
   browser-pane text (`--rendered`, section 2.3.11 only, with fetch_reason; S3 passes). Arizona State: dept
   restrict comes from the CS **MS** handbook 2026-27 (SCAI lists no undergraduate handbook); collaboration and
   disclosure come from the Provost's sample syllabus statements, a Google Doc linked from ai.asu.edu
   (domain_reason). Rice: university "permit with conditions" and disclosure "required" both read from one
   Honor Council sentence (passing AI ideas off as one's own is plagiarism; cue_reason); dept "encourage" from
   department news about COMP 101 (AI built into a course; cue_reason) after C2 refused stance "none found"
   with a positive tone. Eastern Kentucky: university **restrict** from the current required syllabus statement
   ("Unapproved or undisclosed AI use is a violation"; each instructor still picks Prohibited, Conditional or
   Minimally Restricted; the page heads the current set "Fall 2027"); disclosure "required" from 4.1.3ACR, which
   lists AI content without a disclosure statement as plagiarism (cue_reason). Nevada State: no CS department;
   the computing degree is Data Science in the School of Liberal Arts, Sciences, & Business, so that school's
   course policies page is coded as the department ("instructor decides", neutral); se_courses "no public
   syllabus found" because the program has no software engineering course; collaboration "explicit" from the
   AI page's table of uses (cue_reason). UDC: no AI policy at all; every value but tone comes from the
   library's AI Help Guide on udc.libguides.com (domain_reason): stance "instructor decides" ("Always check
   with your instructor..."), collaboration "explicit" (list of study uses, cue_reason), disclosure
   **required** (unacknowledged AI content "is plagiarism", same reading as Defiance and EKU, cue_reason);
   tone positive from the president's AI Initiative page; se_courses "AI built into the course" from the
   official CSCI 341 course description. UMKC: university **restrict** from the UM System rule on
   at.umsystem.edu (instructor silent means forbidden; domain_reason); disclosure "encouraged" from the
   Conservatory's sample statement ("must properly cite", but it is example language); an October 2026
   university news story on an NSF project putting LLMs into core CS courses was NOT used for the
   department because it is university news, not department text.
   Penn: university "instructor decides" (CETLI), disclosure "encouraged" from the ISC guidance imperative
   "Disclose when..." (the statement says it is not a final policy; cue_reason); se_courses "AI built into the
   course" from the catalog description of CIS 2500 Software Development with AI Coding Agents (same rule as
   Stanford and UDC); a SEAS PDF proposal by four named CIS faculty for that course was NOT used for the
   department (named investigators, not a department statement). College of Charleston: university
   **restrict** from the Honor Code (GAI "when not authorized by the instructor(s)" is cheating); tone
   positive, collaboration explicit ("feedback tool, tutor, or creative partner") and disclosure "encouraged"
   from Academic Affairs' integrity and AI page; the CS department's AI page is about AI as a field of study,
   so not coded; se_courses "no public syllabus found" (CSCI 362 syllabi are 2010 to 2020).
   Westminster (PA): university "permit with conditions" and disclosure "required" from the Academic
   Integrity Policy's cheating and plagiarism lists (handing in AI work "as your own"; same reading as Rice;
   cue_reason); tone neutral; the policy page is in catalog.westminster.edu, which answers curl with HTTP
   202 and an empty body, so it was read in the browser pane and **check S3 was changed** to treat an empty
   202 like a 403 (needs fetch_reason; new test; spec notes it). That check change is itself a judgment call
   for Marcus. Niagara CC (now SUNY Niagara, sunyniagara.edu): university **restrict** from the Student
   Conduct Code (unauthorized AI help is cheating), although the college AI Policy (on its TeamDynamix IT
   knowledge base, domain_reason) says faculty pick one of the approved syllabus statements (same pattern as
   WV Wesleyan); disclosure required from the AI Policy; se_courses "no public syllabus found" (the CS A.S.
   has no software engineering course, as at Nevada State). **Checker bug fixed:** the domain was the last
   two parts of the web address, so Niagara became `suny.edu` and Maine Fort Kent `maine.edu`; now kept as
   the campus subdomain for six college-system domains (spec notes it; new test).
   Temple: university **restrict** from the teaching center's Faculty Guide (the provost's blanket policy: AI
   prohibited unless an instructor grants permission; the Student Conduct Code lists unauthorized AI software use as
   dishonesty); tone **positive** from the Student Success Center (the policy's goal is to let students explore AI
   while protecting learning; a judgment call, the faculty guide is balanced); collaboration "in passing" (sample
   statement's permitted-use list starts with brainstorming); disclosure **encouraged** from sample syllabus language
   that says "must be properly documented and cited" (example language, same reading as UMKC; cue_reason).
   Nova Southeastern: university **restrict** from the Student Handbook (October 2026): AI use without the faculty
   member's prior permission "is expressly prohibited" (the quote stops before that phrase because the sentence is
   over 40 words; cue_reason); tone positive from the teaching center ("Generative AI is transforming teaching and
   learning"); collaboration "not discussed" (the "intelligent partner" wording is about faculty work, as at Niagara);
   disclosure "not stated" (left to each course). nova.edu/ai, which claims to hold the university AI policy, gave
   curl HTTP 404, so nothing is coded from it.
   Maine Fort Kent: every value comes from the "AI at UMFK" library guide on umfk-umm.libguides.com
   (domain_reason; its home tab is the official "UMFK Generative Artificial Intelligence (AI) Use Guidance"; the
   university's own site is now umfk.edu, not umfk.maine.edu). University "instructor decides"; tone **positive**
   ("can be transformative", a balanced page, same reading as Nova); disclosure **required** ("Students need to
   clearly cite", the codebook lists "need to" as a must-cue); collaboration "in passing" from a sample syllabus
   statement the guide borrowed from another school (brainstorming, same reading as Temple); se_courses "no public
   syllabus found" (no software engineering course; COS 333 Systems Analysis & Design is the closest). The UMS
   Student Conduct Code treats unattributed AI work as plagiarism; noted, not coded.
   Berry: no college-wide AI policy; every value but se_courses comes from the library's guides on
   libguides.berry.edu (on domain). University "instructor decides" from "Berry's syllabus statement" quoted in the
   faculty guide; tone neutral; collaboration "in passing" (brainstorm; "Copilot" there is a product name);
   disclosure "encouraged" ("highly recommended ... be completely transparent"). The catalog's Academic Standards
   page gave curl HTTP 202 with an empty body; deleted, not read in the browser (the search result showed no AI text).
   Tidewater: university **restrict** from the 2024 Code of Student Rights & Responsibilities (unauthorized AI is
   cheating, same reading as Niagara); disclosure **required** from its plagiarism rule (AI without acknowledgment;
   cue_reason); tone **positive** from the library student guide ("a valuable tool, but..."; balanced page, same
   reading as Nova); se_courses "no public syllabus found" (no software engineering course). **The newer Student
   Code of Conduct, Policy 2214 (July 2025), was NOT read:** curl got 403 and the browser pane turned it into a
   download prompt for Marcus (not taken). If it changed the AI rule, the stance could differ.
   Case Western: university **restrict** from the 2026-27 Academic Integrity Policy (AI "without instructor
   permission" is a violation; cue_reason), although the October 2026 UTech AI policy leaves uses to each
   syllabus; tone positive (Provost: CWRU "embraces AI in education"); collaboration "not discussed"; disclosure
   required (UTech policy: students "must ... disclose and cite permitted AI assistance"); se_courses **"allowed
   with conditions"** from the CSDS 293 Software Craftsmanship statement in the university's published survey of
   faculty syllabus statements (the instructor's text, not a full syllabus; CSDS 293 is a software development
   course, not CSDS 393 Software Engineering, which had nothing public).
   **Inconsistency to raise with Marcus:** Stanford and UDC code an official catalog course description
   that mentions AI as the course page ("AI built into the course"), while EKU, UMKC and an earlier school
   (values.json "CSC 310") treat a description with no AI text as "no public syllabus found", not "not
   addressed". The two readings do not match; one rule should be chosen and applied to all.
- C3_compact: RESOLVED 2026-11-11 evening. Two compacts (15:59, 16:12) over-counted; all 3 over-count compacts
  followed a reply with a thinking block. Marcus chose "Allow, list the gap" (decisions.md; phase-1 spec amendment).
- `save_page.py` adds the date prefix itself: name pages `ai-guidance`, not `2026-11-11-ai-guidance` (15:52 slip,
  copies deleted and saved again). grab.py and showtext.py need `python -I -X utf8` (`-I` ignores PYTHONIOENCODING).
- Rice: news.rice.edu and tss.rice.edu answer curl with HTTP 406; esther.rice.edu syllabi need a login.
- C2 needs dept_stance and dept_tone to be "none found" together: if department text gives a tone, it must
  also give a stance.
- Maricopa sites (gccaz.edu, maricopa.edu) answer curl with 403: read them in the browser pane, as done.
- Small colleges: run the `allowed_domains` searches right after the fixed four, and ALWAYS run the two
  second searches with their exact query text (15:35: I almost logged them as run when they were not).
- Expected failures while coding, not bugs: `check_study.py` with no `--only` shows one PASS per coded school and a FAIL ("school
  not coded yet"); `build.py` exits 1 on C5 only, because the newest web run failed the Ohio-count test (6 Ohio in
  sample.csv, 5 coded). Both clear once all 21 are coded and a web run passes. Check every other build line is PASS.
- Helpers in the scratchpad (not in the repo; folder
  `C:/Users/junni/AppData/Local/Temp/claude/3662653f92cacdd2/a9056776-4951-4636-a9ad-acb1dbccb955/scratchpad`):
  `grab.py [--pat REGEX] [--max N] <archives>` prints AI sentences using the checker's own text extraction;
  `add_school.py <school.json>` puts one school into values.json (ensure_ascii, indent 1, as the file already is)
  and runs the checker on it; school drafts are `s_<unitid>.json`.
- Per school: 4 required searches in parallel; save pages with save_page.py; grab.py for quotes; write
  search-log.md; run the 2 second searches whenever a value is "none found" or "no public syllabus found"
  (nearly always, departments are silent); write s_<unitid>.json; add_school.py; cost row in pilot-cost.md.
  Department stance comes from department-level pages only; course pages feed se_courses only.
- Mistake to avoid (15:23): a Python heredoc with Windows backslashes in an f-string failed, and the commit after
  it ran anyway. Check each step's exit code before committing.

## Phase 5 coding (21 schools, round robin; done)
- Draw done 15:17:54 (seed pushed 15:17:25 in 1cd06c0). sample.csv has 36 rows; round 1 unchanged byte for byte;
  second run identical. Study tests: mutation `validation/runs/2026-11-11T20-18-06-773Z_study.json` (1 failed),
  clean `2026-11-11T20-18-09-258Z_study.json` (38/38). Web run `2026-11-11T20-18-19-940Z_web.json` fails 1
  test (Research note counts 6 Ohio in sample.csv, 5 coded): expected until Case Western is coded.
- Commit locally while coding; push only when web tests pass again (a red CI run blocks the deploy).
- `check_study.py --only X` overwrites checks.json with only X: run the full checker before any commit of checks.json.
- Coding order (done ones get ticked in `progress/pilot-cost.md`, "Phase 5" table): 1 Iowa State 153603,
  2 Stanford 243744, 3 NYIT 194091, 4 West Virginia Wesleyan 237969, 5 Glendale CC 104708, 6 Arizona State
  104151, 7 Rice 227757, 8 Eastern Kentucky 156620, 9 Nevada State 441900, 10 UDC 131399, 11 UMKC 178402,
  12 Penn 215062, 13 College of Charleston 217819, 14 Westminster 216807, 15 Niagara CC 193946, 16 Temple
  216339, 17 Nova Southeastern 136215, 18 Maine Fort Kent 161235, 19 Berry 139144, 20 Tidewater 233772,
  21 Case Western 201645 (Ohio).

- Marcus asked to add schools before the evaluation (15:08:57) and chose 20 more, 6 per type (15:10:24).
- Spec `specs/phase-5-more-schools.md`: round-2 seed 20261115 named in the spec and pushed before any draw; approved 15:15:40 with one more Ohio school (random from Ohio S2: Case Western or Dayton).

## Phase 3 done: Marcus's checklist ticked 2026-11-11T12:22:58-05:00 from his screenshots

## Phase 3 tabs built (11:58 to 2026-11-11T12:11:20-05:00 Nov 11; 5-hour 74% to 85%)
- Spec: `specs/phase-3-interfaces.md`. All four tabs read repository files at build time through
  `web/src/data.js`; pages in `web/src/tabs/`; tests in `web/src/tabs.test.jsx` (20 tests, real data).
- Pushed as 862b16f. Recorded: web 37/37 (`validation/runs/2026-11-11T17-10-16-827Z_web.json`),
  pipeline 13/13 (`2026-11-11T17-07-57-189Z_pipeline.json`), mutation "Ohio added into national
  counts" failed 2 tests (`2026-11-11T17-07-38-873Z_web.json`).
- Fixed on the way (each written up in the spec): 7 malformed `usage.md` rows (build.py now rejects
  them); text-fragment links now carry the whole quote (first,last words highlighted the wrong MIT
  passage; checked in the browser pane); study cells that do not apply show n/a, not FAIL; three
  runs recorded while STATE.md still said Phase 2 had their phase corrected to 3 with a
  `correction` field saying so.
- Dev server: `C:\Claude Folder\.claude\launch.json` entry `project2-web` (outside the repo; the
  preview tool reads only that folder), then open `http://localhost:5173/Project-2-AI-Use-In-Schools/`.

## Phase 2 done (wrap-up 11:28 to 2026-11-11T11:33:07-05:00 Nov 11; 5-hour 69% to 71%)
- R1 re-fetch: `study/refetch.py` fetches every archived URL again with save_page.py's exact curl
  command into a temp folder, compares SHA-256, and for changed pages looks for every coded quote in
  the new copy. Report: `data/coded/refetch-report.md` and `.json`. Final run: 69 pages, 41
  unchanged, 26 changed (HTML that changes bytes per load), 2 refused (HTTP 403, no coded quotes),
  **0 coded quotes missing**. Some sites (Johns Hopkins teaching pages) answer 403 on one run and 200
  on the next; a 403 is reported as "refused", not "gone". Follow-up notes, including a browser-pane
  check of the Johns Hopkins guidelines page, live in `data/coded/refetch-notes.md` and are copied
  into the report on every run.
- Recorded at Phase 2 end: web 17/17 (`validation/runs/2026-11-11T16-32-19-757Z_web.json`), pipeline
  12/12 (`2026-11-11T16-32-23-272Z_pipeline.json`), study 33/33 (`2026-11-11T16-32-24-131Z_study.json`);
  the mutation run (S2 disabled, 1 failed) is `2026-11-11T15-20-17-071Z_study.json`. check_study: all
  15 PASS. All four acceptance boxes in `specs/phase-2-study.md` are ticked.
- Marcus's 3-step checklist (in the spec) was handed to him at Phase 2 end; not yet confirmed done.

## Main coding done (11:16 to 11:24 Nov 11; 5-hour 59% to 66%)
- `check_study.py` with no `--only`: all 15 PASS, "All checks pass: True" (11:24:02). Study tests
  33/33 recorded (`validation/runs/2026-11-11T16-24-02-902Z_study.json`).
- Ohio State 204796: university **restrict** (ai.osu.edu Responsible Use: GenAI for coursework only
  with each instructor's explicit permission; cue_reason), tone positive (AI Fluency FAQ). CSE site
  cse.osu.edu gives curl 403; read in the browser pane (no AI rule), dept "none found" from the search
  log. The official CSE 3231 syllabus site (syllabi.engineering.osu.edu) is curl 403 and the browser
  pane is refused: se_courses "no public syllabus found".
- Baldwin Wallace 201195: all absences (handbook revised Aug 2026 and the 2026-27 catalog honesty
  policy say nothing on AI; catalog.bw.edu gives curl HTTP 202 empty, read in the browser pane).
- Defiance 202514: the only rule is the library's AI guide: restrict ("Unauthorized use ... is
  considered cheating"), cautionary, disclosure **required** ("necessary to cite"; cue_reason).
- Columbus State 202222: Standard Syllabus Statement: restrict ("may not use ... unless explicitly
  permitted"), neutral, disclosure required. se_courses **prohibited**: the CSCI 2221 Spring 2026
  syllabus (Word file) has no course rule and adopts the college statement by reference (cue_reason).
  This is the one judgment call worth Marcus's eye.
- A time typed from memory slipped into the Baldwin Wallace cost row and was replaced with a
  `date -Iseconds` reading (marked "written late").

## Main coding, earlier batches
- Le Moyne-Owen 220604, Luzerne 213659, Cincinnati 201885 coded and passing (11:09 to 11:14; 5-hour
  52% to 57%). Le Moyne-Owen: all absences (handbook and catalog say nothing on AI). Luzerne: the AI
  rule is in the Academic Honesty Policy, a **Word file**; `save_page.py` now saves Word files as
  `.docx`, `study/docx_text.py <archive>` writes the `.docx.txt` the checker reads (like a PDF's
  sidecar), new test, study 33/33 (`validation/runs/2026-11-11T16-12-28-115Z_study.json`).
  Cincinnati: the software engineering course site (uc3093c.github.io) is 404, so se_courses is
  "no public syllabus found".
- Small colleges again returned no own-domain pages from the fixed searches; run the two extra
  `allowed_domains` searches (policy/handbook, CS program/catalog) right after the fixed six.
- Virginia 234076, MIT 166683, Presbyterian 218539 coded and passing (11:00 to 11:06; 5-hour 45% to
  49%, about 1.3 points per school). Rows in `progress/pilot-cost.md`, "Main coding".
- Virginia: the CS department site (engineering.virginia.edu) gives curl HTTP 403 and the browser
  pane could not open it ("navigation denied or failed"); department coded "none found" from the
  search log, with a note saying so. Do not retry it with browser headers.
- Presbyterian: the fixed searches returned no presby.edu pages at all; extra searches with
  `allowed_domains: ["presby.edu"]` found the Blue Book and catalog. Use `allowed_domains` early for
  small colleges.
- Lessons: `unitid` in values.json is a **string** (an int made the checker say "not coded yet");
  for a PDF the value's `archive` is the `.pdf`, not the `.pdf.txt`; the checker joins HTML text
  pieces with a space, so a quote ending right after `</strong>` or `</em>` fails S1 on the period
  (drop the trailing period).

## Deadline and pace
- Everything is due **2 PM EST, Thu Nov 12 2026** (Marcus, 2026-11-11).
- Weekly limit 10% (resets Tue Nov 17 01:00 EST). **The 5-hour window is the real constraint**:
  it went 10% to 22% from 10:00 to 10:21 Nov 11 while context grew 78k to 198k. It resets 14:40 EST.
- Marcus wants a `/compact` prepared at every phase end and after each big chunk (CLAUDE.md).
- Marcus asked (10:15 Nov 11): **no Coaching sections** any more, despite the global CLAUDE.md
  rule and the per-turn hook; and no plan mode. "Let's just try and get this done properly."

## Earlier notes (all done; kept for the record)
Phase 4 is done: Marcus confirmed all four checklist steps at 2026-11-11T15:03:10-05:00. Phase-end reading at 2026-11-11T15:02:53-05:00
(5-hour 8%, weekly 22%, context 157,588), marked "just before /compact".
1. Take a usage reading marked "after /compact" (full 7-column row in the main table of
   `progress/usage.md`, phase 5) and run build.py, checking its exit code (a crash once went
   unnoticed behind a pipe to tail). Every row in `progress/log.md` needs 5 columns, evidence last.
2. Phase 5 Evaluation belongs to Marcus (`specs/00-project.md`: "Marcus's evaluation, reflection,
   presentation"; exit check "Marcus"). Ask him what he wants from Claude for it before doing
   anything; per CLAUDE.md, a phase spec is written before the phase starts.
3. Deadline 2 PM EST Thu Nov 12 2026. Never `git checkout` a file holding uncommitted work.

## Phase 4 done (12:27 to 15:03 Nov 11; details in `specs/phase-4-validation.md`)
- 22 claims in `validation/claims.json`, each backed by a test, file or dated outside source;
  `web/src/claims.test.jsx` fails on any unregistered sentence. Pipeline checks C5 (claims' tests
  passed in the newest run) and C6 (each mutation followed by a passing run); counter of test
  commands run without the recorder; C3 rule for a /compact after a stopped turn.
- `validation/caught.json`: 15 errors caught outside test runs, shown on the Validation tab.
- Recorded: web 48/48 (`validation/runs/2026-11-11T19-54-19-977Z_web.json`), pipeline 17/17
  (`2026-11-11T19-47-59-829Z_pipeline.json`); mutations `2026-11-11T17-42-18-324Z_web.json` and
  `2026-11-11T17-42-41-129Z_web.json`. Twelve findings written up in the spec.

## Pilot result (details and costs in `progress/pilot-cost.md`)
- Minnesota 174066, Johns Hopkins 162928, Valparaiso 152600, Coppin State 162283, Snow 230597:
  coded and all pass `check_study.py`. Average 2.6 five-hour points and about 35,800 tokens of
  context per school, falling as the procedure settled. Projection: the 10 left take about 35
  points with compacts; 5-hour was 40% at 10:52 and resets 14:40 EST.
- **Codebook v2 adopted** (all four pilot candidates; reasons in `study/codebook.md`, "Changes in
  version 2"): pre-2023 course pages count as "no public syllabus found"; example syllabus language
  telling students to disclose is "encouraged"; news on the department site is department text;
  a rule against only "inappropriate or excessive" use is "permit with conditions" ("unauthorized"
  use is "restrict"). Recoded the pilot (spec R2): one value changed (Johns Hopkins `se_courses`),
  saved in `data/coded/codebook-v2-recode.json`. `values.json` and `codebook.json` say version 2.
- Check S3 changed during the pilot: browser text (`--rendered`) passes with a raw curl copy at
  HTTP 200, or at HTTP 403 plus a written `fetch_reason` on the value (spec and test updated; sabotage
  run failed exactly the new test). Not yet needed by any coded value.
- `.gitattributes` stores `data/sources/**` byte-for-byte (`-text`); without it git rewrote line
  endings in archives, which would break S2 hashes on a fresh checkout.
- Helpers: a scratch text viewer (`showtext.py` in the session scratchpad
  `C:/Users/junni/AppData/Local/Temp/claude/3662653f92cacdd2/a9056776-4951-4636-a9ad-acb1dbccb955/scratchpad/`:
  `python -I showtext.py <file> [regex] [maxchars]` prints a saved page's visible text filtered by
  a regex) and `pdftotext -enc UTF-8 <pdf> <pdf>.txt` for the PDF sidecar. For PDFs, `grep -o -iE
  ".{0,120}(pattern).{0,120}"` on the .txt; never print whole sections (one 45-line print cost 8k tokens).
- `save_page.py` adds the file extension itself: name a PDF `student-handbook`, not `student-handbook.pdf`.
- Do NOT retry curl with extra browser headers when a site returns 403: the permission system refused
  it as bot-check circumvention. Read such pages in the browser pane instead.
- ddc7d76a: checked with Marcus's permission (metadata only); it is the retired canon-keeper project
  (Sep 9), not this one. Closed.
- Prompts: Marcus reaffirmed at 10:47 that all his prompts are published in full (public repo,
  `data/derived/contributions.json`); he may ask to hide some later. Hiding later does not remove
  them from git history.

## Where things stand
- Phases 0 and 1: done. Live site still a skeleton:
  https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
- Phase 2 spec `specs/phase-2-study.md`: approved 10:15 Nov 11. **No hand-coding by Marcus**;
  quality is shown by the 10 automated checks in the spec (S1 to S5, C1 to C4, N1, plus R1 and R2).
- Done in Phase 2: IPEDS 2024 frame (`data/frame/`, 1,509 schools, 5 strata, 2025 Carnegie), 15
  schools drawn (`data/frame/sample.csv`, seed 20261111). The pre-clear plan (CIP 11.07 only)
  would have excluded Ohio State and Cincinnati; fixed with 11.0701 or 11.0101.
- Codebook v1 frozen: `study/codebook.json` (allowed values, cue words, required searches) and
  `study/codebook.md` (rules). Variables: univ_stance, univ_tone, dept_stance, dept_tone,
  collaboration, disclosure, se_courses.
- Tools: `study/save_page.py` (curl archive plus `.meta.json` with status, final URL, SHA-256;
  `--rendered` for JavaScript pages, needs a raw curl copy of the same URL too),
  `study/check_study.py` (writes `data/coded/checks.json`). Commands in the project CLAUDE.md.
- Tests: study 32/32 (latest `validation/runs/2026-11-11T15-53-30-496Z_study.json`); earlier study 31/31 (mutation run with S2 disabled failed exactly the S2 test; restored), pipeline
  12/12, web 17/17; all recorded. CI runs all three suites before deploy (pushed 5ccc209).

## How to code one school (spec task 4; same for the pilot and the 10 left)
For each school, slug `<unitid>-<short name>` (e.g. `174066-minnesota`):
1. Run the 4 required searches from `codebook.json` with WebSearch, `{domain}` = the domain above.
   Write `data/sources/<slug>/search-log.md`: one `## Search: <exact query>` heading per search, then
   one `- <url> (what it was; opened or not; saved as ...)` line per relevant result, or
   `- no relevant results`. The checker needs every heading and at least one line under each.
2. Find the university AI guidance page and the CS department pages (spec "Fixed search").
3. Save each page behind a value with `save_page.py`. Open the saved file's text to copy quotes
   exactly (quotes at most 40 words). If curl gets a 403 or an empty JavaScript shell, save the
   browser pane's text with `--rendered` (the raw curl copy must also exist with HTTP 200).
4. Add the school to `data/coded/values.json`:
   `{"codebook_version": 2, "schools": [{"unitid", "slug", "name", "values": {var: entry}}]}`.
   Entry with evidence: value, quote, url, archive (repo-relative path), source_type, optional
   cue_reason, optional domain_reason. Absence entry: value plus `reviewed` (list of archive paths)
   or `search_log` (path). For every "none found" or "no public syllabus found", also run and log
   the 2 `second_searches`.
5. Run `check_study.py --only <unitid>`; fix until it passes. Note time and a get_usage reading per
   school in `progress/pilot-cost.md` (time taken, 5-hour points, context growth).
Codebook is frozen at version 2 for the 10 remaining schools. A further change would be version 3,
with reasons in `codebook.md`, and every coded school recoded (spec R2); avoid it unless a rule is wrong.

## Still open
- Nothing waiting on Marcus.

## Sessions in this project
| Session | Started in | Model | Covers |
|---|---|---|---|
| 0cf9c9ad-b66c-4406-998d-e6e34b8c2e47 | `C:\Claude Folder` (transcript under `~/.claude/projects/C--Claude-Folder/`) | claude-opus-5 until 00:14:38 Nov 8, then claude-opus-5-5 | planning, audit, Phase 0, first /compact (Nov 8 00:57), Phase 1, ends with the /clear |
| a9056776-4951-4636-a9ad-acb1dbccb955 | `C:\Claude Folder` (same folder) | claude-opus-5-5 | starts after the /clear (Nov 11 10:00:07); Phase 2 |

## Known quirks
- Shell tool: several heredocs in one command failed to parse, and double backslashes collapse to
  one. Write prose and Markdown with the file-writing tool; keep backslash escapes out of code
  (build them with `chr(92)` in Python if needed).
- The session's working directory is `C:\Claude Folder`, one level above the repo; use absolute paths.
- Claude's browser pane ignores reload keys. Prove fresh loads with a marker instead.
- The Claude app shows Marcus no context-token number. Never write a checklist step that needs one.
