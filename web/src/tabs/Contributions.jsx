import { useState } from 'react'
import { contributions, easternDay, easternTime, isMarcus } from '../data.js'

const ENTRIES = contributions.entries
const replyByTurn = Object.fromEntries(ENTRIES.filter((e) => e.kind === 'reply').map((e) => [e.turn, e]))
const KINDS = [...new Set(ENTRIES.map((e) => e.kind))].sort()
const PHASES = ['planning', '0', '1', '2', '3', '4', '5'].filter((p) => ENTRIES.some((e) => e.phase === p))
const who = (e) => (isMarcus(e.actor) ? 'Marcus' : 'Claude')

function Counts() {
  const rows = ['Marcus', 'Claude'].map((name) => {
    const mine = ENTRIES.filter((e) => who(e) === name)
    const byKind = KINDS.map((k) => [k, mine.filter((e) => e.kind === k).length]).filter(([, n]) => n)
    return { name, total: mine.length, byKind }
  })
  return (
    <ul className="stats" data-from="data/derived/contributions.json">
      {rows.map((r) => (
        <li key={r.name}>
          <strong>{r.total}</strong> entries by {r.name}:{' '}
          {r.byKind.map(([k, n]) => `${n} ${n === 1 ? k : k.replace(/y$/, 'ie') + 's'}`).join(', ')}
        </li>
      ))}
    </ul>
  )
}

function Entry({ e, nestReplies }) {
  const reply = nestReplies && e.kind === 'prompt' ? replyByTurn[e.turn] : null
  return (
    <li className="entry" data-testid="entry" data-actor={who(e)}>
      <div className="entry-head">
        <time dateTime={e.time}>{easternTime(e.time)}</time>
        <span className={`badge ${who(e).toLowerCase()}`}>{e.actor}</span>
        <span className="kind">
          {e.kind}
          {e.turn ? ` ${e.turn}` : ''}
        </span>
        <span className="muted">Phase {e.phase}</span>
      </div>
      <p className="entry-text">{e.text}</p>
      {e.kind === 'decision' && e.options ? <p className="muted">Options: {e.options}</p> : null}
      {e.notes ? <p className="muted">{e.notes}</p> : null}
      {e.evidence ? <p className="muted">Evidence: {e.evidence}</p> : null}
      {e.commit ? (
        <p className="muted">
          Commit <code>{e.commit}</code>
          {e.note ? ` (${e.note})` : ''}
        </p>
      ) : null}
      {reply ? (
        <details className="reply">
          <summary>
            Claude’s reply ({easternTime(reply.time)}
            {reply.toolCalls ? `, after ${reply.toolCalls} tool calls` : ''})
          </summary>
          <p className="entry-text">{reply.text}</p>
        </details>
      ) : null}
    </li>
  )
}

export default function Contributions() {
  const [filters, setFilters] = useState({ actor: 'all', kind: 'all', phase: 'all', query: '' })
  const set = (key) => (ev) => setFilters({ ...filters, [key]: ev.target.value })
  const q = filters.query.trim().toLowerCase()
  // Replies sit under the prompt they answer. They are listed on their own only when the view is
  // limited to Claude or to replies, where the prompt itself is filtered out.
  const nestReplies = filters.actor !== 'Claude' && filters.kind !== 'reply'
  const shown = ENTRIES.filter(
    (e) =>
      (!nestReplies || e.kind !== 'reply') &&
      (filters.actor === 'all' || who(e) === filters.actor) &&
      (filters.kind === 'all' || e.kind === filters.kind) &&
      (filters.phase === 'all' || e.phase === filters.phase) &&
      (!q || e.text.toLowerCase().includes(q) || (nestReplies && replyByTurn[e.turn]?.text.toLowerCase().includes(q))),
  )
  const days = []
  for (const e of shown) {
    const day = easternDay(e.time)
    if (days.at(-1)?.day !== day) days.push({ day, entries: [] })
    days.at(-1).entries.push(e)
  }

  return (
    <>
      <p data-claim="contributions-source">
        Built by <code>pipeline/build.py</code> from this project’s Claude Code transcripts (Marcus’s
        prompts and commands, Claude’s replies), <code>progress/log.md</code> (milestones),{' '}
        <code>progress/decisions.md</code> (Marcus’s decisions) and the git history (commits). Every
        prompt is published in full, as Marcus decided. Times are Eastern.
      </p>
      <Counts />
      <div className="filters" role="search">
        <label>
          Who{' '}
          <select value={filters.actor} onChange={set('actor')}>
            <option value="all">everyone</option>
            <option value="Marcus">Marcus</option>
            <option value="Claude">Claude</option>
          </select>
        </label>
        <label>
          Kind{' '}
          <select value={filters.kind} onChange={set('kind')}>
            <option value="all">all</option>
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </label>
        <label>
          Phase{' '}
          <select value={filters.phase} onChange={set('phase')}>
            <option value="all">all</option>
            {PHASES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Search <input type="search" value={filters.query} onChange={set('query')} />
        </label>
      </div>
      <p className="muted" aria-live="polite" data-from="data/derived/contributions.json">
        Showing {shown.length} entries.
      </p>
      {days.map((d) => (
        <section key={d.day} className="day" data-from="data/derived/contributions.json">
          <h2>{d.day}</h2>
          <ol className="timeline">
            {d.entries.map((e, i) => (
              <Entry key={`${e.time}-${e.kind}-${i}`} e={e} nestReplies={nestReplies} />
            ))}
          </ol>
        </section>
      ))}
    </>
  )
}
