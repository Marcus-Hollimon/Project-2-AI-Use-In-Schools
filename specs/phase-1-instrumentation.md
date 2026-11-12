# Phase 1: Instrumentation

Goal: turn this project's Claude Code transcripts into two small, publishable data files, one for
the Contributions tab (deliverable 3) and one for the Token usage tab (deliverable 4). Every figure
in them is checked against a number our code did not produce.

Status: approved by Marcus 2026-11-08T01:21-05:00, with the publishing rule as described. He chose "publish all".

## Known before any code (measured 2026-11-08 after the first /compact)
Script and output: `evidence/phase1-recon/`. Transcript timestamps are UTC; EST is UTC minus 5.
1. A `/compact` is recorded as a `system` record with subtype `compact_boundary`, followed by a
   `user` record with `isCompactSummary: true`. Ours: manual, 305,065 tokens before, 14,969
   after, took 56.5 s, at 00:57:16 EST.
2. Its "tokens before" equals the last response's context plus that response's output, exactly
   (304,338 + 727 = 305,065).
3. **The compaction's own model call leaves no record in the transcript**: no `api-request`, no
   usage. Transcript totals cannot see what a compact costs; only the plan readings can. The
   Token usage tab must show this as a labeled gap.
4. The app's context reading agrees with the transcript: 5 of 5 readings within 281 tokens
   (0.18%) of a response's context size, one exact (81,551).
5. Every model call also writes an `api-request` record, so responses can be counted a second,
   independent way (65 requests vs 64 responses; the extra one was the call in flight).
6. After the compact, the first response wrote 34,474 tokens into the cache (a cache rebuild);
   after that each turn read about 80k tokens instead of about 304k.
7. About 78k of the 81.5k tokens left after the compact are fixed overhead sent on every turn
   (tool definitions 37.5k, MCP tools 20.4k, system prompt 9.9k, skills 5.8k, MCP instructions
   2.4k), as the app reported at 00:57:55.
8. How a `/clear` appears (found 2026-11-11, after Marcus's `/clear` between 09:59:41 and
   10:00:07 EST): it starts a new session with a new id and a new transcript file
   (`a9056776-4951-4636-a9ad-acb1dbccb955.jsonl`, same folder, same cwd). Neither file records
   the `/clear` itself: the old file just stops after its last turn (no marker record), and the
   new file's first message has no parent. So from transcripts alone a `/clear` cannot be told
   apart from opening a new session; the pipeline labels it "new session or /clear", and the
   `usage.md` row names which one it was.

## Definitions
- **Response**: one model call, identified by `message.id`. Counted once across all files.
- **Token classes** (four, always shown separately): input (uncached), cache write, cache read,
  output. Thinking tokens are part of output and shown as a sub-line, never added on top.
- **Context size** of a response: input + cache write + cache read.
- **Phase** of a response: the phase of the latest reading in `progress/usage.md` at or before it.
  `usage.md` is the single source of phase boundaries. Earlier responses count as "planning".
- **Practice segment** (the "by practice" view): the stretch between two context resets (session
  start, `/compact`, `/clear`, resume). Per segment: responses, the four classes, average context
  per response, and which reset ended it.
- **Turn**: one prompt from Marcus plus everything Claude did until his next prompt.

## Tasks
1. `pipeline/`: a Python 3.12 project managed by uv 0.11.13, with pytest pinned in the lockfile.
   Before writing tests, sparse-clone pytest's docs at the installed version into `reference/`.
2. `pipeline/sessions.json`: the explicit list of this project's session ids and transcript
   folders. The script reads only those files, plus any `<session>/subagents/*.jsonl`. It never
   lists or opens other projects' sessions.
3. `pipeline/build.py` writes three files to `data/derived/` and prints a plain-English summary:
   - `tokens.json`: per response (time, session, model, phase, segment, four classes, thinking);
     totals per segment and per phase; reset events with before and after tokens; the plan
     readings from `usage.md`; known gaps (each compaction's own call).
   - `contributions.json`: timeline entries with time, actor (Marcus or Claude), kind, and text.
     Kinds: Marcus's prompt, Claude's final reply for that turn, tool calls in that turn (count
     only), milestones from `log.md`, decisions from `decisions.md`, commits from `git log`.
     Commits use Marcus's git identity but carry a `Co-Authored-By: Claude` trailer; label them
     "written by Claude, pushed from Marcus's account", not as Marcus's own work.
   - `checks.json`: the results of C1 to C4 below, for the Validation tab.
4. Privacy filter, applied before anything reaches `data/derived/`: no tool inputs or outputs, no
   file contents, no images, no thinking text, nothing from `api-request-blob` records; the home
   folder path becomes `~`; the email address is removed. Prompt and reply text is published only
   after Marcus has read `private/qa-preview.md` (gitignored, his computer only) and listed any
   turns to hide in `progress/prompt-exclusions.json`.
5. Tests on small made-up transcripts (committed) that each contain one known trap:
   - one response saved as several rows that repeat the same usage (count once)
   - the same response in two files after a resume (count once)
   - a compact boundary (starts a new segment; records a gap)
   - an `api-request` with no response yet (in flight)
   - `user` records that are not Marcus's prompts: tool results, the compact summary, slash-command
     output, hook output, system reminders
   - a resumed session's copied prompts (no duplicate questions)
6. Recorded runs: `pipeline/record_tests.py` writes `validation/runs/<time>_pipeline.json` in the
   same shape as the web runs. One deliberate mutation run (dedup broken, a test must fail),
   then a clean run.
7. CI runs the pipeline tests before the build, so a failing test blocks deployment. CI has no
   transcripts, so it runs the tests only, not `build.py`.
8. Update `CLAUDE.md` and `STATE.md` with the commands.

## Cross-checks (each against a number our code did not produce)
- **C1 Context**: for every `usage.md` reading with a context value, some response has a context
  size within 0.5% of the app's number, timed within 2 minutes of the reading.
- **C2 Completeness**: per session, `api-request` records equal unique responses. One extra is
  allowed, only in the live session, only as its newest record.
- **C3 Compact**: each compact boundary's "tokens before" equals the last response's context plus
  its output, exactly.
- **C4 Inflation shown**: the naive row sum is reported beside the deduplicated figure, so the
  correction is visible rather than asserted.
- Plan readings are whole percents. They are shown beside the token figures with no claim of
  precision, and are the only measure of what a compaction costs.
- **Amendment to C2 (2026-11-08T01:40-05:00, Claude, reported to Marcus)**: the first real run
  failed C2 because one request at 00:13:13 EST had no response; another request followed 0.6 s
  later with no error record, most likely a retry. C2 now also accepts requests that are followed
  by another request with no response in between, but only by listing each one by time in
  `checks.json` and as a known gap in `tokens.json`. Nothing is dropped silently.
- **Amendment to C1 (2026-11-11T09:54-05:00, Claude, reported to Marcus)**: the reading taken at
  09:52 on Nov 11 (224,386) failed the 0.5% rule. The response that took it wrote a large file,
  and the app's number fell between that response's context (222,907) and the next one's
  (226,004). The app's exact formula is unknown (a guess, "context plus output minus thinking",
  matched none of 10 readings). New rule: each reading must lie between the context sizes of two
  consecutive responses, the first within 2 minutes of the reading. All 10 readings pass it. The
  nearest single-response difference is still reported in `checks.json`. Same day, a first run
  had also failed because Claude wrote the reading time as 09:55 instead of 09:52; the check
  caught that, and the time was corrected.
- **Amendment to C3 (2026-11-11 evening, decided by Marcus; see `progress/decisions.md`)**: two
  compacts (15:59 and 16:12 EST) reported 721 and 415 more tokens than the last response's context
  plus output. Of all 20 real compacts, the 3 that missed the exact rule (including the 12:45 one
  already excused as a stopped turn) are exactly the 3 that followed a response with a thinking
  block, which the transcript keeps only as a signature; all 17 others matched exactly. The gap
  does not track the signature's length (1.4 to 4.1 characters per token), so it cannot be computed.
  New rule: a compact also passes when tokens-before is larger and the last response had a
  thinking block; the difference is listed in `checks.json`. Same evening, C2 began failing on an
  app placeholder reply ("No response requested.", model `<synthetic>`, zero usage, no request);
  such records are no longer counted as responses (a counting fix, not a rule change).

## Acceptance checks
Claude runs these and records the results:
- [x] A recorded pipeline test run passes; a recorded mutation run fails.
- [x] C1, C2 and C3 pass on the real transcripts; results saved in `data/derived/checks.json`.
- [x] Searching `data/derived/` for the home folder path, the email address, and tool output finds
      nothing.
- [x] CI runs the pipeline tests, and the deploy still succeeds.
- [x] Web tests still pass, recorded.

Marcus's checklist, for the END of Phase 1 (do it yourself, then tick and date each line). None of
these files or commands exist until Claude has finished the tasks above; Claude will say when the
checklist is ready and hand over the exact PowerShell commands then.
- [x] Run the commands Claude gives you in PowerShell. (2026-11-11, Marcus: ran fine, all checks
      PASS, screenshot.) The second half, "compare with the context number the app shows", could
      not be done: the app shows Marcus no context number. Claude wrote this step without checking
      what the app displays. Replaced by Claude adding the app's own reading at 09:46:57 to
      `usage.md`; check C1 then matched it within 648 tokens (0.31%). That is Claude's check, not an
      independent human one, and is recorded as such.
- [x] Read `private/qa-preview.md`. (2026-11-11, Marcus: "It's all fine"; publish all stands.)
- [x] Pick one of your prompts in the preview. Its time roughly matches when you sent it.
      (Covered by Marcus's "all fine"; he did not mention the time check separately.)
- [x] On GitHub, `validation/runs/` has a run whose name ends in `_pipeline.json`. (2026-11-11,
      Marcus: screenshot shows four.)

## End of phase: the deliberate /clear
1. Claude updates `STATE.md`, commits and pushes, and records a reading "just before /clear".
2. Marcus types `/clear`.
3. First thing afterwards (start of Phase 2): a reading "after /clear"; find the new session's id
   and add it to `sessions.json`; re-run `build.py`; record how the `/clear` shows up. Then write
   the Phase 2 spec.

## Budget
Phase 0 cost 10 five-hour points and 1 weekly point. At the start of this phase: 5-hour 31%
(resets 04:30 EST), weekly 53% (resets Tue Nov 10 01:00 EST). Target: at most 15 five-hour points.

## Out of scope
- The web tabs themselves (Phase 3). This phase only produces their data.
- Other projects' transcripts, in any form.
