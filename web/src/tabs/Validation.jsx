import { useState } from 'react'
import {
  CAUGHT,
  CLAIMS,
  CLAIM_RESULTS,
  MUTATION_RESULTS,
  MUTATION_RUNS,
  RUNS,
  SCHOOLS,
  STUDY_CHECKS,
  TEST_COMMANDS,
  TEST_GROUPS,
  eastern,
  filterRuns,
  groupStudyTests,
  newestRun,
  repoFile,
  studyChecks,
  survivors,
} from '../data.js'
import { REPO_URL, TABS } from '../routes.js'

const phases = [...new Set(RUNS.map((r) => r.phase))].sort()
const suites = [...new Set(RUNS.map((r) => r.suite))].sort()
const failedRuns = RUNS.filter((r) => r.summary.failed > 0)
// A mutation run's label starts with "mutation" ("clean run after restoring mutations" is not one).
const isMutation = (r) => /^mutation/i.test(r.label)
const tabLabel = Object.fromEntries(TABS.map((t) => [t.id, t.label]))

// Phase 6: what the tests check, how we know they catch errors, and what they cannot check.
function HowTestsWork() {
  const study = newestRun('study')
  const pipeline = newestRun('pipeline')
  const web = newestRun('web')
  const groups = groupStudyTests(study)
  const toolTests = (groups.tool ?? []).length
  const sampleTests = (groups.sample ?? []).length
  const first = MUTATION_RUNS[0]
  const last = MUTATION_RUNS.at(-1)
  // The newest study run before the first mutation run: the test count the mutation tool started from.
  const studyBefore = RUNS.find((r) => r.suite === 'study' && new Date(r.startedAt) < new Date(first.startedAt))
  const added = study.summary.total - studyBefore.summary.total - toolTests
  const left = survivors(last)
  const rows = [
    ...STUDY_CHECKS.map(([id, text]) => [id, id, text]),
    ...TEST_GROUPS,
  ].filter(([id]) => groups[id])
  return (
    <section className="how" aria-labelledby="how-tests-work">
      <h2 id="how-tests-work">How the tests work</h2>
      <p data-claim="validation-how-intro">
        No set of tests can be proven to catch every possible mistake, because nobody can list every
        possible mistake. What this section shows is narrower, and every part of it can be checked: what
        each test checks, that the tests were seen to fail when the thing they guard was broken on
        purpose, and what no test here can check.
      </p>

      <h3>Three layers</h3>
      <ol className="layers" data-claim="validation-how-layers">
        <li>
          <strong>The data.</strong> <code>study/check_study.py</code> checks every coded value at every
          school against its saved page and the codebook (checks S1 to N1, defined at the bottom of this
          page): {studyChecks.schools.filter((s) => s.pass).length} of {studyChecks.schools.length} schools
          pass.
        </li>
        <li>
          <strong>The code that checks and counts.</strong> The newest study run has {study.summary.total}{' '}
          tests: {study.summary.total - toolTests - sampleTests} test the checker, most by building a small
          made-up school that breaks exactly one rule and confirming the checker catches it; {toolTests}{' '}
          test the mutation tool and {sampleTests} the random draw of the sample. The newest pipeline run
          has {pipeline.summary.total} tests of the code that counts tokens and builds the timeline.
        </li>
        <li>
          <strong>The pages.</strong> The newest web run has {web.summary.total} tests of what the pages
          show: they recompute the numbers on this site from the data files and compare them with the
          page, and check that links, filters and menus work.
        </li>
        <li>
          <strong>What ties them together.</strong> The claims register below lists all {CLAIMS.length}{' '}
          factual sentences on the site, each with the test, file or outside page that backs it.
        </li>
      </ol>

      <h3>How we know the tests catch errors</h3>
      <p data-claim="validation-how-mutations">
        A test that never fails proves nothing, so the tests were broken on purpose, in two ways. By hand:{' '}
        {failedRuns.filter(isMutation).length} recorded runs had a bug planted to see a particular test
        notice it, and each did (listed under “Errors caught” below). Automatically:{' '}
        <a href={repoFile('study/mutation_score.py')}>a mutation tool</a> made {last.total} copies of the
        study checker, each with one small planted bug (a comparison turned around, “and” swapped for “or”,
        a “not” dropped, True swapped for False, a number made one larger, a function returning nothing,
        “break” swapped for “continue”), and ran the study tests on each copy. A bug counts as caught when
        at least one test fails.
      </p>
      <ul className="stats mutation" data-claim="validation-how-mutations">
        <li>
          <strong>
            {first.killed} of {first.total}
          </strong>{' '}
          caught in the first run ({eastern(first.startedAt)})
        </li>
        <li>
          <strong>{added}</strong> study tests then added to close the gaps it found
        </li>
        <li>
          <strong>
            {last.killed} of {last.total}
          </strong>{' '}
          caught in the newest run ({eastern(last.startedAt)})
        </li>
      </ul>
      <p data-claim="validation-how-mutations">
        The {left.length} planted bugs the newest run did not catch, each with what it would change:
      </p>
      <table
        className="data survivors"
        aria-label="Planted bugs not caught"
        data-from="validation/mutation-runs validation/mutation-triage.json"
      >
        <thead>
          <tr>
            <th scope="col">Planted bug</th>
            <th scope="col">Verdict</th>
            <th scope="col">Why</th>
          </tr>
        </thead>
        <tbody>
          {left.map((m) => (
            <tr key={m.id} data-testid="survivor">
              <th scope="row">
                {m.function}, line {m.line}: <code>{m.before}</code> to <code>{m.after}</code>
              </th>
              <td>{m.triage?.verdict ?? 'NO VERDICT WRITTEN'}</td>
              <td>{m.triage?.why ?? ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p data-claim="validation-how-mutations">
        The tool does not try {last.notTried.join('; ')}. Its score says how well the tests catch the kinds
        of bug it plants, not every kind.{' '}
        <a href={repoFile(`validation/mutation-runs/${last.file}`)}>Every planted bug in the newest run</a>.
      </p>

      <h3>Edge cases, check by check</h3>
      <p data-claim="validation-how-edge">
        Every test in the newest study run, under the check it tests. This shows which unusual cases are
        covered, instead of claiming that all of them are.
      </p>
      <table className="data edge" aria-label="Edge cases tested, by check" data-from="validation/runs">
        <thead>
          <tr>
            <th scope="col">Check</th>
            <th scope="col">What it checks</th>
            <th scope="col">Cases tested</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([id, label, text]) => (
            <tr key={id} data-testid="edge-row">
              <th scope="row">{label}</th>
              <td>{text}</td>
              <td>
                <ul>
                  {groups[id].map((t) => (
                    <li key={t.name} className={t.status}>
                      {t.text}
                    </li>
                  ))}
                </ul>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>What no test here can prove</h3>
      <ul className="limits" data-claim="validation-how-limits">
        <li>
          That a stance or tone is the right reading of a page. The tests prove that each quote is on the
          saved page word for word and contains a cue word the codebook lists for its value; they cannot
          prove that a second person would read the page the same way. No second coder was used (Marcus’s
          decision).
        </li>
        <li>
          Anything about schools outside the {SCHOOLS.length} studied. The groups are too small to stand for
          all US departments.
        </li>
        <li>What is behind a login, such as course sites and private syllabi, which the study could not see.</li>
        <li>
          That a page still says the same thing today. Each value is checked against the copy saved on the
          day it was coded; the re-check on the Research page fetched every page again and counts the
          quotes no longer there.
        </li>
        <li>Bugs of kinds nobody thought to test for. The mutation score measures only the kinds it plants.</li>
      </ul>
    </section>
  )
}

function ClaimEvidence({ claim }) {
  const results = CLAIM_RESULTS.filter((r) => r.claim === claim.id)
  return (
    <ul className="evidence">
      {(claim.tests ?? []).map((t) => {
        const r = results.find((x) => x.suite === t.suite && x.test === t.test)
        return (
          <li key={t.suite + t.test} className={r ? (r.pass ? 'ok' : 'bad') : ''}>
            Test ({t.suite}): {t.test}
            {r ? (
              <>
                {' '}
                · {r.status} in{' '}
                {r.run ? <a href={repoFile(`validation/runs/${r.run}`)}>the newest {t.suite} run</a> : 'no run'}
              </>
            ) : (
              ' · not yet checked by the pipeline'
            )}
          </li>
        )
      })}
      {(claim.files ?? []).map((f) => (
        <li key={f}>
          File: <a href={repoFile(f)}>{f}</a>
        </li>
      ))}
      {(claim.sources ?? []).map((src) => (
        <li key={src.url}>
          Outside source: <a href={src.url}>{new URL(src.url).hostname}</a> (checked {eastern(src.checked)}):{' '}
          {src.says}
        </li>
      ))}
    </ul>
  )
}

function Claims() {
  const [tab, setTab] = useState('all')
  const [kind, setKind] = useState('all')
  const shown = CLAIMS.filter((c) => (tab === 'all' || c.tab === tab) && (kind === 'all' || c.kind === kind))
  const passed = CLAIM_RESULTS.filter((r) => r.pass).length
  return (
    <>
      <h2>Claims and their evidence</h2>
      <p data-claim="validation-claims">
        Every sentence on this site that states a fact is listed here with what backs it: a test, a file
        in the repository, or an outside page with the date it was checked. A test fails if a sentence
        on the site is missing from this list or names evidence that does not exist, and the pipeline’s
        check C5 needs every test named here to have passed in the newest recorded run of its suite (
        {passed} of {CLAIM_RESULTS.length} did at the last build).
      </p>
      <div className="filters" role="search">
        <label>
          Page{' '}
          <select value={tab} onChange={(e) => setTab(e.target.value)}>
            <option value="all">all</option>
            {TABS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Kind{' '}
          <select value={kind} onChange={(e) => setKind(e.target.value)}>
            <option value="all">all</option>
            <option value="computed">computed</option>
            <option value="method">method</option>
            <option value="external">external</option>
          </select>
        </label>
      </div>
      <table
        className="data claims"
        aria-label="Claims and their evidence"
        data-from="validation/claims.json data/derived/checks.json"
      >
        <thead>
          <tr>
            <th scope="col">Claim</th>
            <th scope="col">Page</th>
            <th scope="col">Kind</th>
            <th scope="col">Evidence</th>
          </tr>
        </thead>
        <tbody>
          {shown.map((c) => (
            <tr key={c.id} data-testid="claim">
              <th scope="row">{c.claim}</th>
              <td>{tabLabel[c.tab]}</td>
              <td>{c.kind}</td>
              <td>
                <ClaimEvidence claim={c} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}

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
      <ul className="stats" data-from="validation/runs data/coded/checks.json">
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

      <HowTestsWork />

      <Claims />

      <h2>Every recorded test run</h2>
      <p data-claim="validation-scope">
        Every run made through the test recorder is saved the moment it finishes, pass or fail, in{' '}
        <code>validation/runs/</code>. Not in this list: the runs GitHub makes before every deploy (see
        the <a href={`${REPO_URL}/actions`}>Actions history</a>), and {TEST_COMMANDS.unrecorded} test
        commands Claude ran during development without the recorder, counted from the transcripts (
        {TEST_COMMANDS.recorded} went through the recorder).
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
      <p className="muted" aria-live="polite" data-from="validation/runs">
        Showing {shown.length} of {RUNS.length} runs.
      </p>
      <div className="runs" data-from="validation/runs">
        {shown.map((r) => (
          <RunItem key={r.file} run={r} />
        ))}
      </div>

      <h2>Errors caught</h2>
      <p data-claim="validation-mutations">
        Runs where a test failed. {failedRuns.filter(isMutation).length} of {failedRuns.length} were
        deliberate “mutations”: a bug planted on purpose to prove that a test notices it. Each is
        followed by a passing run of the same suite once the bug is removed (pipeline check C6:{' '}
        {MUTATION_RESULTS.filter((m) => m.pass).length} of {MUTATION_RESULTS.length} confirmed at the last build).
        A test that never fails proves nothing.
      </p>
      <ul className="caught" aria-label="Errors caught" data-from="validation/runs">
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

      <h2>Errors caught outside test runs</h2>
      <p data-claim="validation-caught-outside">
        Problems found by lint, by a pipeline check on the real data, by reading, in the browser, or by
        Marcus, rather than by a recorded test run. Each says who found it, the fix, and what guards
        against it now.
      </p>
      <ul className="caught outside" aria-label="Errors caught outside test runs" data-from="validation/caught.json">
        {CAUGHT.map((c) => (
          <li key={c.time + c.what}>
            <strong>{eastern(c.time)}</strong> · Phase {c.phase} · {c.foundBy}: {c.what}
            <br />
            <span className="muted">
              How: {c.how} Fix: {c.fix} Guard: {c.guard} Evidence:{' '}
              {c.evidence.map((f, i) => (
                <span key={f}>
                  {i ? ', ' : ''}
                  <a href={repoFile(f)}>{f}</a>
                </span>
              ))}
              .
            </span>
          </li>
        ))}
      </ul>

      <h2>Study checks, per school</h2>
      <p data-claim="validation-study">
        Run by <code>study/check_study.py</code> on every coded value (last run{' '}
        {eastern(studyChecks.generatedAt)}).{' '}
        <a href={repoFile('data/coded/checks.json')}>Every individual finding</a>.
      </p>
      <dl className="check-defs" data-claim="validation-study">
        {STUDY_CHECKS.map(([id, text]) => (
          <div key={id}>
            <dt>{id}</dt>
            <dd>{text}</dd>
          </div>
        ))}
      </dl>
      <table className="data" aria-label="Study checks per school" data-from="data/coded/checks.json">
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
