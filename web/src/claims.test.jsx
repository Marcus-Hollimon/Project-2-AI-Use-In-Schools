// Phase 4 tests: every factual sentence on the site is in the claims register (validation/claims.json)
// with evidence that exists, and the numbers stated in prose are recomputed here from the files.
import { cleanup, render, screen, within } from '@testing-library/react'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { afterEach, describe, expect, test } from 'vitest'
import App from './App.jsx'
import { SCHOOLS, eastern, resetRows } from './data.js'
import { TABS, hashFor } from './routes.js'

const ROOT = resolve(process.cwd(), '..') + '/'
const readJson = (p) => JSON.parse(readFileSync(ROOT + p, 'utf-8'))
const register = readJson('validation/claims.json').claims
const caught = readJson('validation/caught.json').entries
const pipelineChecks = readJson('data/derived/checks.json')
const tokens = readJson('data/derived/tokens.json')

function open(id) {
  window.location.hash = hashFor(id)
  return render(<App />)
}

// Every page, rendered once: the elements marked as claims and the text elements on it.
function eachPage(fn) {
  for (const t of TABS) {
    const { container } = open(t.id)
    fn(t.id, container.querySelector('main'))
    cleanup()
  }
}

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

// The test names defined in a suite's source files, read as text (each suite has its own syntax).
function testNames(suite) {
  const read = (dir, re) =>
    readdirSync(ROOT + dir)
      .filter((f) => re.test(f))
      .map((f) => readFileSync(ROOT + dir + f, 'utf-8'))
      .join('\n')
  if (suite === 'web') {
    const src = read('web/src/', /\.test\.jsx$/)
    return new Set([...src.matchAll(/test\(\s*(['"])((?:\\.|(?!\1).)*)\1/g)].map((m) => m[2].replace(/\\(.)/g, '$1')))
  }
  const src = read(suite === 'pipeline' ? 'pipeline/tests/' : 'study/tests/', /^test_.*\.py$/)
  return new Set([...src.matchAll(/^def (test_\w+)/gm)].map((m) => m[1]))
}

describe('Claims register', () => {
  test('every marked claim on the pages is in the register, and every register entry is on its tab', () => {
    const ids = new Set(register.map((c) => c.id))
    expect(ids.size).toBe(register.length)
    const found = {}
    eachPage((tab, main) => {
      for (const el of main.querySelectorAll('[data-claim]')) {
        // "none" is allowed only on the small labels above a page title, which state no fact.
        if (el.dataset.claim === 'none') {
          expect(el.className, el.textContent).toBe('eyebrow')
          continue
        }
        expect(ids, `unregistered claim "${el.dataset.claim}" on ${tab}`).toContain(el.dataset.claim)
        found[el.dataset.claim] = tab
      }
    })
    for (const c of register) expect(found[c.id], `claim ${c.id} not found on its tab`).toBe(c.tab)
  })

  test('every paragraph, list item and definition on every page is a registered claim or drawn from a named file', () => {
    const unmarked = []
    eachPage((tab, main) => {
      for (const el of main.querySelectorAll('p, li, dd, dt, blockquote, caption')) {
        if (!el.closest('[data-claim], [data-from]')) unmarked.push(`${tab}: ${el.textContent.slice(0, 80)}`)
      }
      for (const el of main.querySelectorAll('[data-from]')) {
        for (const path of el.dataset.from.split(' ')) expect(existsSync(ROOT + path), path).toBe(true)
      }
    })
    expect(unmarked).toEqual([])
  })

  test('every claim names evidence that exists: files, test names in their suite, outside sources with a date', () => {
    const names = { web: testNames('web'), pipeline: testNames('pipeline'), study: testNames('study') }
    for (const c of register) {
      expect(['computed', 'method', 'external']).toContain(c.kind)
      expect((c.tests ?? []).length + (c.files ?? []).length + (c.sources ?? []).length, c.id).toBeGreaterThan(0)
      for (const f of c.files ?? []) expect(existsSync(ROOT + f), `${c.id}: ${f}`).toBe(true)
      for (const t of c.tests ?? []) expect(names[t.suite], `${c.id}: ${t.suite} test "${t.test}"`).toContain(t.test)
      for (const s of c.sources ?? []) {
        expect(s.url).toMatch(/^https:\/\//)
        expect(s.checked).toMatch(/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[-+]\d\d:\d\d$/)
        expect(s.says.length).toBeGreaterThan(20)
      }
      if (c.kind === 'external') expect((c.sources ?? []).length, c.id).toBeGreaterThan(0)
    }
  })

  test('the claims table lists every register entry with its C5 result', () => {
    open('validation')
    const rows = screen.getAllByTestId('claim')
    expect(rows).toHaveLength(register.length)
    const results = pipelineChecks.C5_claims ?? []
    register.forEach((c, i) => {
      expect(within(rows[i]).getByRole('rowheader').textContent).toBe(c.claim)
      for (const t of c.tests ?? []) {
        const r = results.find((x) => x.claim === c.id && x.suite === t.suite && x.test === t.test)
        expect(rows[i].textContent).toContain(r ? `${t.test} · ${r.status}` : `${t.test} · not yet checked`)
      }
    })
  })

  test('every entry in caught.json is complete and its evidence exists', () => {
    expect(caught.length).toBeGreaterThan(0)
    for (const e of caught) {
      for (const k of ['time', 'phase', 'foundBy', 'what', 'how', 'fix', 'guard']) expect(e[k], k).toBeTruthy()
      expect(e.time).toMatch(/^\d{4}-\d\d-\d\dT\d\d:\d\d(:\d\d)?[-+]\d\d:\d\d$/)
      for (const f of e.evidence) expect(existsSync(ROOT + f), f).toBe(true)
    }
    open('validation')
    const list = screen.getByRole('list', { name: 'Errors caught outside test runs' })
    expect(list.querySelectorAll(':scope > li')).toHaveLength(caught.length)
  })
})

describe('Numbers stated in prose', () => {
  test('the Research note counts the Ohio schools Marcus chose from sample.csv', () => {
    const csv = readFileSync(ROOT + 'data/frame/sample.csv', 'utf-8').trim().split(/\r?\n/).slice(1)
    const ohio = csv.filter((l) => l.startsWith('ohio,'))
    const chosen = ohio.filter((l) => l.split(',')[1] === 'fixed by Marcus').length
    expect(chosen).toBe(SCHOOLS.filter((s) => s.how === 'fixed by Marcus').length)
    open('research')
    expect(screen.getByRole('note').textContent).toContain(
      `${ohio.length} in Ohio (${chosen} chosen by Marcus, ${ohio.length - chosen} at random)`,
    )
  })

  test('the re-check line matches refetch-report.json', () => {
    const report = readJson('data/coded/refetch-report.json')
    const quotes = report.rows.flatMap((r) => r.quotes ?? []).length
    const missing = report.coded_quotes_missing_from_new_copy
    expect(report.rows.length).toBe(report.pages)
    open('research')
    const line = document.querySelector('[data-claim="research-refetch"]').textContent
    expect(line).toContain(`all ${report.pages} saved pages`)
    expect(line).toContain(`${quotes - missing} of ${quotes} quotes`)
    expect(line).toContain(`${missing} are missing`)
  })

  test('the run list states the unrecorded test commands counted by the pipeline', () => {
    const counts = pipelineChecks.testCommands
    expect(counts.recorded + counts.unrecorded).toBeGreaterThan(0)
    open('validation')
    const text = document.querySelector('[data-claim="validation-scope"]').textContent
    expect(text).toContain(`${counts.unrecorded} test commands Claude ran during development without the recorder`)
    expect(text).toContain(`(${counts.recorded} went through the recorder)`)
    expect(text).not.toMatch(/Nothing is left out/)
  })

  test('every prompt is published: the hide list is empty', () => {
    expect(readJson('progress/prompt-exclusions.json').hide).toEqual([])
    const prompts = readJson('data/derived/contributions.json').entries.filter((e) => e.kind === 'prompt')
    expect(prompts.filter((p) => p.text === '[hidden by Marcus]')).toEqual([])
  })

  test('cache reads are the largest token class', () => {
    const [largest] = tokens.classes.toSorted((a, b) => tokens.totals[b] - tokens.totals[a])
    expect(largest).toBe('cacheRead')
  })

  test('every phase has a first reading, and every reset with no reading just before it is named on the page', () => {
    const phases = new Set(tokens.readings.map((r) => r.phase))
    for (const p of ['planning', '0', '1', '2', '3', '4']) expect(phases, `phase ${p}`).toContain(p)
    const rows = resetRows()
    expect(rows.filter((r) => r.kind === '/compact')).toHaveLength(tokens.resets.length)
    expect(rows.filter((r) => r.kind === '/clear').length).toBeGreaterThan(0)
    for (const r of rows) expect(new Date(r.before.time) < new Date(r.after.time)).toBe(true)
    const missed = rows.filter((r) => !r.before.moment.includes('just before'))
    open('tokens')
    const text = document.querySelector('[data-claim="tokens-readings"]').textContent
    if (missed.length === 0) expect(text).toContain('Every reset has a reading taken just before it.')
    for (const r of missed) expect(text).toContain(`${r.kind} of ${eastern(r.time)}`)
    expect(text.match(/ of [A-Z][a-z]{2} \d/g) ?? []).toHaveLength(missed.length)
  })
})
