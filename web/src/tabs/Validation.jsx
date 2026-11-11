import { useState } from 'react'
import { RUNS, STUDY_CHECKS, eastern, filterRuns, repoFile, studyChecks } from '../data.js'

const phases = [...new Set(RUNS.map((r) => r.phase))].sort()
const suites = [...new Set(RUNS.map((r) => r.suite))].sort()
const failedRuns = RUNS.filter((r) => r.summary.failed > 0)
const isMutation = (r) => /mutation/i.test(r.label)

function RunItem({ run }) {
  const failed = run.tests.filter((t) => t.status === 'failed')
  return (
    <details className="run" data-testid="run">
      <summary>
        <span className={run.summary.failed ? 'badge fail' : 'badge pass'}>
          {run.summary.failed ? `${run.summary.failed} failed` : 'all passed'}
        </span>
        <span className="run-title">
          {run.suite} · Phase {run.phase} · {run.summary.passed}/{run.summary.total} passed
        </span>
        <span className="muted">
          {eastern(run.startedAt)}
          {run.label ? ` · ${run.label}` : ''}
        </span>
      </summary>
      <p className="muted">
        Command <code>{run.command}</code> on commit <code>{run.gitCommit}</code>
        {run.uncommittedChanges ? ' (plus changes not yet committed)' : ''} ·{' '}
        <a href={repoFile(`validation/runs/${run.file}`)}>recorded file</a>
      </p>
      {run.correction ? <p className="muted">Correction noted in the file: {run.correction}</p> : null}
      {failed.length ? (
        <ul className="failures">
          {failed.map((t) => (
            <li key={t.name}>
              <strong>{t.name}</strong>
              <pre>{t.failureMessages.join('\n').slice(0, 1200)}</pre>
            </li>
          ))}
        </ul>
      ) : null}
      <ul className="tests">
        {run.tests.map((t) => (
          <li key={t.name} className={t.status}>
            {t.status === 'passed' ? '✓' : '✗'} {t.name}
          </li>
        ))}
      </ul>
    </details>
  )
}

export default function Validation() {
  const [filters, setFilters] = useState({ phase: 'all', suite: 'all', status: 'all', query: '' })
  const set = (key) => (e) => setFilters({ ...filters, [key]: e.target.value })
  const shown = filterRuns(RUNS, filters)
  const tests = RUNS.reduce((n, r) => n + r.summary.total, 0)

  return (
    <>
      <ul className="stats">
        <li>
          <strong>{RUNS.length}</strong> recorded test runs
        </li>
        <li>
          <strong>{tests.toLocaleString('en-US')}</strong> test results
        </li>
        <li>
          <strong>{failedRuns.length}</strong> runs with a failure
        </li>
        <li>
          <strong>{studyChecks.schools.filter((s) => s.pass).length}</strong> of {studyChecks.schools.length}{' '}
          schools pass the study checks
        </li>
      </ul>

      <h2>Every recorded test run</h2>
      <p>
        Each run is saved by the test recorder the moment it finishes, pass or fail, in{' '}
        <code>validation/runs/</code>. Nothing is left out.
      </p>
      <div className="filters" role="search">
        <label>
          Phase{' '}
          <select value={filters.phase} onChange={set('phase')}>
            <option value="all">all</option>
            {phases.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Suite{' '}
          <select value={filters.suite} onChange={set('suite')}>
            <option value="all">all</option>
            {suites.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status{' '}
          <select value={filters.status} onChange={set('status')}>
            <option value="all">all</option>
            <option value="passed">all passed</option>
            <option value="failed">had failures</option>
          </select>
        </label>
        <label>
          Search{' '}
          <input
            type="search"
            value={filters.query}
            onChange={set('query')}
            placeholder="label or test name"
          />
        </label>
      </div>
      <p className="muted" aria-live="polite">
        Showing {shown.length} of {RUNS.length} runs.
      </p>
      <div className="runs">
        {shown.map((r) => (
          <RunItem key={r.file} run={r} />
        ))}
      </div>

      <h2>Errors caught</h2>
      <p>
        Runs where a test failed. {failedRuns.filter(isMutation).length} of {failedRuns.length} were
        deliberate “mutations”: a bug planted on purpose to prove that a test notices it, then removed
        (the next run passes). A test that never fails proves nothing.
      </p>
      <ul className="caught" aria-label="Errors caught">
        {failedRuns.map((r) => (
          <li key={r.file}>
            <strong>{eastern(r.startedAt)}</strong> · {r.suite} · {r.label || 'no label'}:{' '}
            {r.tests
              .filter((t) => t.status === 'failed')
              .map((t) => t.name)
              .join('; ')}
          </li>
        ))}
      </ul>

      <h2>Study checks, per school</h2>
      <p>
        Run by <code>study/check_study.py</code> on every coded value (last run{' '}
        {eastern(studyChecks.generatedAt)}).{' '}
        <a href={repoFile('data/coded/checks.json')}>Every individual finding</a>.
      </p>
      <dl className="check-defs">
        {STUDY_CHECKS.map(([id, text]) => (
          <div key={id}>
            <dt>{id}</dt>
            <dd>{text}</dd>
          </div>
        ))}
      </dl>
      <table className="data" aria-label="Study checks per school">
        <thead>
          <tr>
            <th scope="col">School</th>
            {STUDY_CHECKS.map(([id]) => (
              <th scope="col" key={id}>
                {id}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {studyChecks.schools.map((s) => (
            <tr key={s.unitid}>
              <th scope="row">{s.name}</th>
              {STUDY_CHECKS.map(([id]) =>
                s.checks[id] === undefined ? (
                  <td key={id} className="na" title="nothing of this kind to check for this school">
                    n/a
                  </td>
                ) : (
                  <td key={id} className={s.checks[id] ? 'ok' : 'bad'}>
                    {s.checks[id] ? 'pass' : 'FAIL'}
                  </td>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
