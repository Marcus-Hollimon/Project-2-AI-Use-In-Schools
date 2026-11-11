# Decisions

Decisions Marcus made, with what was on the table. Times Eastern (EST). Source: session transcript
0cf9c9ad, where the answers are recorded verbatim.

| Time | Decision | Options considered | Chosen by | Notes |
|---|---|---|---|---|
| 2026-11-08T00:13:13-05:00 | Study design: stratified sample of about 40 schools | Stratified ~40 (Claude's recommendation) · narrow and deep, 20 to 30 · broad and shallow, 100+ | Marcus | At 00:22 Claude advised piloting 5 schools first and setting the final number from measured cost per school. Final number open until Phase 2. |
| 2026-11-08T00:13:13-05:00 | UI authorship: Claude writes the UI, Marcus reviews | Claude writes, Marcus reviews (recommendation) · Marcus designs, Claude wires up · split | Marcus | Recorded in the project CLAUDE.md. |
| 2026-11-08T00:13:13-05:00 | Web technology: React with a build step | Static site (recommendation) · React with a build step · Python server | Marcus, against Claude's recommendation | At 00:22 Claude agreed React is reasonable. The deployment risk was retired first, in Phase 0. |
| 2026-11-08T00:13:13-05:00 | Priority if time runs short: the study and its findings dashboard | Study (recommendation) · all four evenly · validation | Marcus | |
| 2026-11-08T00:14:38-05:00 | Use Opus 5.5, as the teacher suggested | | Marcus | Transcripts record the model per response, so the switch is visible in the token data. |
| 2026-11-08T00:15:56-05:00 | Remove canon-keeper from the global CLAUDE.md | | Marcus | Backup kept. |
| 2026-11-08T00:27:41-05:00 | Start Phase 0, including removing the canon-keeper test hook | Start Phase 0 · keep the hook | Marcus | |
| 2026-11-08T00:51-05:00 | Context resets use `/compact`, not `/clear` | `/clear` (Claude's suggestion) · `/compact` | Marcus | Claude cannot trigger `/compact`; Marcus types it at boundaries Claude prepares. Deliverable 4 compares the two, so one deliberate `/clear` is still proposed (open). |
| 2026-11-08T00:53:40-05:00 | One deliberate `/clear`, at the end of Phase 1; `/compact` everywhere else | One `/clear` (Claude's suggestion) · compact only | Marcus | Gives deliverable 4 a real clear-vs-compact comparison. Placed after Phase 1 so STATE.md has already been tested once. |
| 2026-11-08T01:21-05:00 | Phase 1 spec approved, including the publishing rule | approve · change | Marcus | Work on Phase 1 tasks starts. |
| 2026-11-08T01:21-05:00 | Publish all question-and-answer turns | publish all · hide some after reading the preview | Marcus | Decided before the preview existed. The privacy filter still applies (no tool output, file contents, images, thinking; home path and email removed), and the preview is still generated so he can change his mind before the first publish. |
| 2026-11-11T09:51-05:00 | Deadline is 2 PM Nov 12 for everything, not midnight | (information from Marcus) | Marcus | Replaces the Nov 10, 11, 12 split in specs/00-project.md. |
| 2026-11-11T09:51-05:00 | Study sample: 15 schools, popular Ohio schools plus some big national names (Harvard named as an example) | stratified ~40 (earlier plan) · 15 chosen by Marcus | Marcus | A chosen (purposive) sample, not a random or stratified one: findings describe these 15 schools only and cannot be generalized to US CS departments. Exact list proposed in the Phase 2 spec for his approval. |
| 2026-11-11T09:51-05:00 | Compact at good points, relatively frequently, to save tokens | (instruction from Marcus) | Marcus | Claude prepares a /compact at every phase end and after each big chunk of work. The planned /clear at the end of Phase 1 still happens. |
