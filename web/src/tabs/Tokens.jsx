import { CLASS_LABELS, eastern, fmt, phaseRows, pipelineChecks, resetRows, tokens } from '../data.js'

const CLASSES = tokens.classes
const inflation = pipelineChecks.C4_inflation
const ratio = (inflation.naive.cacheRead / inflation.deduplicated.cacheRead).toFixed(2)

function resetSummary(rows) {
  const after = (kind) => rows.filter((r) => r.kind === kind).map((r) => r.after.context)
  const compacts = after('/compact')
  const clears = after('/clear')
  if (!compacts.length || !clears.length) return null
  return (
    <p data-claim="tokens-resets">
      After a <strong>/clear</strong> the next reading showed {clears.map(fmt).join(', ')} tokens of
      context; after a <strong>/compact</strong> it showed {fmt(Math.min(...compacts))} to{' '}
      {fmt(Math.max(...compacts))}. Both throw away the conversation; a /compact keeps a written
      summary of it, so it starts slightly larger but keeps the thread. Most of what is left after
      either is fixed overhead sent with every message (tool definitions, system prompt, skills).
      The plan-limit cost of a reset cannot be separated from the work around it: the 5-hour figure is
      read in whole percent, and the /compact’s own model call is missing from the transcript (see
      gaps below).
    </p>
  )
}

export default function Tokens() {
  const resets = resetRows()
  const missedBefore = resets.filter((r) => r.noReadingJustBefore)
  const checks = ['C1_context', 'C2_completeness', 'C3_compact', 'privacy']
  return (
    <>
      <h2>All tokens, deduplicated</h2>
      <table className="data" aria-label="Token totals" data-from="data/derived/tokens.json">
        <thead>
          <tr>
            {CLASSES.map((c) => (
              <th scope="col" key={c}>
                {CLASS_LABELS[c]}
              </th>
            ))}
            <th scope="col">Responses</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            {CLASSES.map((c) => (
              <td key={c} data-class={c}>
                {fmt(tokens.totals[c])}
              </td>
            ))}
            <td>{fmt(tokens.totals.responses)}</td>
          </tr>
        </tbody>
      </table>
      <p data-claim="tokens-thinking-cache">
        Thinking: {fmt(tokens.totals.thinking)} tokens, already counted inside output and never added
        on top. Cache reads dominate because every message re-sends the whole conversation, which the
        cache serves cheaply.
      </p>
      <p className="callout" role="note" data-claim="tokens-dedup">
        <strong>Deduplicated.</strong> The transcripts repeat one response’s usage on several rows, and a
        resumed session copies old rows into a new file. The {fmt(inflation.usageRows)} usage rows hold{' '}
        {fmt(inflation.uniqueResponses)} distinct responses, each counted once. Summing rows instead
        would have shown {fmt(inflation.naive.cacheRead)} cache-read tokens, {ratio} times the real
        figure.
      </p>

      <h2>By phase</h2>
      <table className="data" aria-label="Tokens by phase" data-from="data/derived/tokens.json">
        <thead>
          <tr>
            <th scope="col">Phase</th>
            <th scope="col">Responses</th>
            {CLASSES.map((c) => (
              <th scope="col" key={c}>
                {CLASS_LABELS[c]}
              </th>
            ))}
            <th scope="col">Average context</th>
          </tr>
        </thead>
        <tbody>
          {phaseRows().map(([phase, row]) => (
            <tr key={phase}>
              <th scope="row">{phase}</th>
              <td>{fmt(row.responses)}</td>
              {CLASSES.map((c) => (
                <td key={c}>{fmt(row[c])}</td>
              ))}
              <td>{fmt(row.averageContext)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>/clear compared with /compact</h2>
      {resetSummary(resets)}
      <table className="data" aria-label="Context resets" data-from="data/derived/tokens.json progress/usage.md">
        <thead>
          <tr>
            <th scope="col">Reset</th>
            <th scope="col">Last reading before</th>
            <th scope="col">First reading after</th>
            <th scope="col">Context before → after (readings)</th>
            <th scope="col">Transcript’s own count before → after</th>
            <th scope="col">5-hour % before → after</th>
          </tr>
        </thead>
        <tbody>
          {resets.map((r) => (
            <tr key={r.after.time}>
              <th scope="row">{r.kind}</th>
              <td>
                {eastern(r.before.time)}
                {r.noReadingJustBefore && ' (none was taken just before this reset)'}
              </td>
              <td>{eastern(r.after.time)}</td>
              <td>
                {fmt(r.before.context)} → {fmt(r.after.context)}
              </td>
              <td>
                {r.transcriptBefore == null
                  ? 'not recorded for /clear'
                  : `${fmt(r.transcriptBefore)} → ${fmt(r.transcriptAfter)}`}
              </td>
              <td>
                {r.before.fiveHour} → {r.after.fiveHour}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Plan-limit readings</h2>
      <p data-claim="tokens-readings">
        Read from the Claude app’s usage figures at the start of every phase and before and after every
        reset, and written to <code>progress/usage.md</code>. Percentages are whole numbers, as the app shows them.
        {missedBefore.length === 0
          ? ' Every reset has a reading taken just before it.'
          : ` Exceptions: no reading was taken just before the ${missedBefore
              .map((r) => `${r.kind} of ${eastern(r.time)}`)
              .join('; ')}, so the table above shows the last earlier reading.`}
      </p>
      <table className="data" aria-label="Plan-limit readings" data-from="progress/usage.md">
        <thead>
          <tr>
            <th scope="col">Time</th>
            <th scope="col">Phase</th>
            <th scope="col">Moment</th>
            <th scope="col">5-hour %</th>
            <th scope="col">Weekly %</th>
            <th scope="col">Context tokens</th>
            <th scope="col">Reset before this</th>
          </tr>
        </thead>
        <tbody>
          {tokens.readings.map((r) => (
            <tr key={r.time}>
              <td>{eastern(r.time)}</td>
              <td>{r.phase}</td>
              <td>{r.moment}</td>
              <td>{r.fiveHour}</td>
              <td>{r.weekly}</td>
              <td>{fmt(r.context)}</td>
              <td>{r.reset}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Checks on these numbers</h2>
      <ul className="checks" data-claim="tokens-checks">
        {checks.map((id) => {
          const list = pipelineChecks[id]
          const ok = list.every((x) => x.pass)
          return (
            <li key={id} className={ok ? 'ok' : 'bad'}>
              {ok ? '✓' : '✗'} <strong>{id}</strong>: {list.filter((x) => x.pass).length} of {list.length}{' '}
              passed.{' '}
              {
                {
                  C1_context:
                    'Each context figure read from the app lies between two consecutive responses in the transcript, the first within two minutes of the reading: an independent check on the transcript numbers.',
                  C2_completeness:
                    'Every API request in the transcripts has its response counted, apart from listed unanswered retries.',
                  C3_compact:
                    'Each /compact’s “tokens before” equals the last response’s context plus its output, or is larger only after a stopped turn or a reply with hidden thinking (whose size the transcript does not keep); each gap is listed in checks.json.',
                  privacy:
                    'The published files contain no home-folder path, not Marcus’s email address, and no raw tool records.',
                }[id]
              }
            </li>
          )
        })}
      </ul>
      <h3>Known gaps</h3>
      <ul data-from="data/derived/tokens.json">
        {tokens.gaps.map((g) => (
          <li key={g.time + g.what}>
            {eastern(g.time)}: {g.what}
            {g.itRead ? ` (it read about ${fmt(g.itRead)} tokens)` : ''}.
          </li>
        ))}
      </ul>
    </>
  )
}
