import { useState } from 'react'
import {
  SCHOOLS,
  STRATA,
  VARIABLES,
  countTable,
  isAbsence,
  quoteLink,
  refetch,
  repoFile,
  searchLogPath,
} from '../data.js'

const national = SCHOOLS.filter((s) => s.group === 'National').length
const ohio = SCHOOLS.length - national
const perStratum = national / STRATA.length

function CountTable({ variable }) {
  const counts = countTable(variable.id)
  return (
    <table className="data counts" aria-label={variable.label}>
      <caption>{variable.label}</caption>
      <thead>
        <tr>
          <th scope="col">Answer</th>
          {STRATA.map((s) => (
            <th scope="col" key={s.id} title={s.label}>
              {s.id}
            </th>
          ))}
          <th scope="col">National (of {national})</th>
          <th scope="col" className="ohio">
            Ohio (of {ohio})
          </th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(counts).map(([value, row]) => (
          <tr key={value}>
            <th scope="row">{value}</th>
            {STRATA.map((s) => (
              <td key={s.id} className={row[s.id] ? '' : 'zero'}>
                {row[s.id] ?? 0}
              </td>
            ))}
            <td className={row.national ? 'total' : 'total zero'}>{row.national}</td>
            <td className={row.ohio ? 'ohio' : 'ohio zero'}>{row.ohio}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function ValueDetail({ school, variable }) {
  const v = school.values[variable.id]
  const live = v.quote ? quoteLink(v.url, v.quote, v.archive) : null
  return (
    <li className="value-detail">
      <p>
        <strong>{variable.label}:</strong> <span className="pill">{v.value}</span>
        {v.source_type ? <span className="muted"> · {v.source_type}</span> : null}
      </p>
      {v.quote ? (
        <>
          <blockquote>“{v.quote}”</blockquote>
          <p className="links">
            {live ? (
              <a href={live} target="_blank" rel="noreferrer">
                Open the live page at this quote
              </a>
            ) : (
              <a href={v.url} target="_blank" rel="noreferrer">
                Open the live file (use Ctrl+F in the viewer)
              </a>
            )}
            {' · '}
            <a href={repoFile(v.archive)} target="_blank" rel="noreferrer">
              Saved copy
            </a>
          </p>
        </>
      ) : null}
      {isAbsence(v.value) ? (
        <p className="links">
          {(v.reviewed ?? []).map((path) => (
            <span key={path}>
              <a href={repoFile(path)} target="_blank" rel="noreferrer">
                Page reviewed: {path.split('/').pop()}
              </a>
              {' · '}
            </span>
          ))}
          <a href={repoFile(searchLogPath(school.slug))} target="_blank" rel="noreferrer">
            Search log
          </a>
        </p>
      ) : null}
      {v.note ? <p className="muted note-text">Coder’s note: {v.note}</p> : null}
    </li>
  )
}

function SchoolRow({ school }) {
  return (
    <details className="school">
      <summary>
        <span className="school-name">{school.name}</span>
        <span className="muted">
          {school.group} · {school.stratum}
          {school.how === 'fixed by Marcus' ? ' · chosen by Marcus' : ''}
          {school.passedChecks ? ' · all study checks passed' : ' · STUDY CHECKS FAILED'}
        </span>
      </summary>
      <ul className="values">
        {VARIABLES.map((variable) => (
          <ValueDetail key={variable.id} school={school} variable={variable} />
        ))}
      </ul>
    </details>
  )
}

export default function Research() {
  const [group, setGroup] = useState('all')
  const shown = SCHOOLS.filter((s) => group === 'all' || s.group === group)
  const quotes = refetch.rows.flatMap((r) => r.quotes ?? [])
  return (
    <>
      <p className="callout" role="note">
        <strong>Descriptive only.</strong> {national} schools were drawn at random nationally ({perStratum} in
        each of {STRATA.length} strata) and {ohio} in Ohio, reported separately and never added into the
        national counts. Groups this small support counts, not percentages or claims about all US
        departments. Coded on {SCHOOLS[0].coded_at} from public web pages only.
      </p>

      <h2>Answers by question</h2>
      <dl className="strata">
        {STRATA.map((s) => (
          <div key={s.id}>
            <dt>{s.id}</dt>
            <dd>{s.label}</dd>
          </div>
        ))}
      </dl>
      <div className="tables">
        {VARIABLES.map((v) => (
          <CountTable key={v.id} variable={v} />
        ))}
      </div>

      <h2>Every school, with its sources</h2>
      <p>
        Open a school to see the quote behind each answer. “Open the live page at this quote” scrolls
        the school’s page to the sentence and highlights it (current Chrome, Edge, Firefox and
        Safari); “Saved copy” is the page as it was on the day it was coded.
      </p>
      <label className="filter">
        Show{' '}
        <select value={group} onChange={(e) => setGroup(e.target.value)}>
          <option value="all">all {SCHOOLS.length} schools</option>
          <option value="National">national sample</option>
          <option value="Ohio">Ohio sample</option>
        </select>
      </label>
      <div className="schools">
        {shown.map((s) => (
          <SchoolRow key={s.unitid} school={s} />
        ))}
      </div>

      <p className="note">
        Re-checked {new Date(refetch.generated_at).toLocaleDateString('en-US')}: all {refetch.pages}{' '}
        saved pages were fetched again; {quotes.length - refetch.coded_quotes_missing_from_new_copy} of{' '}
        {quotes.length} quotes on pages that had changed are still there, and{' '}
        {refetch.coded_quotes_missing_from_new_copy} are missing.{' '}
        <a href={repoFile('data/coded/refetch-report.md')}>Re-fetch report</a>.
      </p>
    </>
  )
}
