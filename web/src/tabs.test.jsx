// Phase 3 tests: each tab is rendered from the real data files, and its numbers are compared with
// figures taken straight from those files here, independently of the page code.
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { afterEach, describe, expect, test } from 'vitest'
import App from './App.jsx'
import { RUNS, SCHOOLS, VARIABLES, allowedValues, countTable, filterRuns, quoteLink } from './data.js'
import { hashFor } from './routes.js'

// Vitest runs from web/ (its config lives there), so the repository root is one level up.
const ROOT = resolve(process.cwd(), '..') + '/'
const readJson = (p) => JSON.parse(readFileSync(ROOT + p, 'utf-8'))
const values = readJson('data/coded/values.json')
const sample = readFileSync(ROOT + 'data/frame/sample.csv', 'utf-8').trim().split(/\r?\n/).slice(1).map((l) => l.split(','))
const groupOf = Object.fromEntries(sample.map((c) => [c[2], { ohio: c[0] === 'ohio', stratum: c[12] }]))
const contributions = readJson('data/derived/contributions.json')
const tokens = readJson('data/derived/tokens.json')

function open(id) {
  window.location.hash = hashFor(id)
  return render(<App />)
}
const select = (label) => screen.getByLabelText(label, { selector: 'select' })

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

describe('Research findings', () => {
  test('every question adds up to 10 national schools (2 per stratum) and 5 Ohio schools', () => {
    for (const v of VARIABLES) {
      const rows = Object.values(countTable(v.id))
      const sum = (key) => rows.reduce((n, r) => n + (r[key] ?? 0), 0)
      expect([sum('national'), sum('ohio')]).toEqual([10, 5])
      for (const s of ['S1', 'S2', 'S3', 'S4', 'S5']) expect(sum(s)).toBe(2)
    }
  })

  test('each count equals a count taken directly from values.json and sample.csv', () => {
    for (const v of VARIABLES) {
      const table = countTable(v.id)
      for (const value of allowedValues(v.id)) {
        const matching = values.schools.filter((s) => s.values[v.id].value === value)
        expect(table[value].ohio).toBe(matching.filter((s) => groupOf[s.unitid].ohio).length)
        expect(table[value].national).toBe(matching.filter((s) => !groupOf[s.unitid].ohio).length)
      }
    }
  })

  test('the page shows the counts and says the findings are descriptive', () => {
    open('research')
    expect(screen.getByRole('note').textContent).toMatch(/Descriptive only/)
    const t = screen.getByRole('table', { name: 'University stance on student AI use' })
    const restrict = within(t).getByRole('rowheader', { name: 'restrict' }).closest('tr')
    const expected = countTable('univ_stance').restrict
    expect(restrict.lastChild.textContent).toBe(String(expected.ohio))
    expect(restrict.children[6].textContent).toBe(String(expected.national))
  })

  test('every quote has a live link (with a text fragment for web pages) and a saved copy that exists', () => {
    open('research')
    let quotes = 0
    for (const s of values.schools) {
      for (const v of Object.values(s.values)) {
        if (!v.quote) continue
        quotes += 1
        expect(existsSync(ROOT + v.archive)).toBe(true)
        const link = quoteLink(v.url, v.quote, v.archive)
        if (/\.(pdf|docx?)$/i.test(v.archive)) expect(link).toBeNull()
        else expect(link).toContain(':~:text=')
      }
    }
    const fragmentLinks = screen.getAllByRole('link', { name: 'Open the live page at this quote' })
    const fileLinks = screen.queryAllByRole('link', { name: /Open the live file/ })
    expect(fragmentLinks.length + fileLinks.length).toBe(quotes)
    expect(screen.getAllByRole('link', { name: 'Saved copy' })).toHaveLength(quotes)
  })

  test('every "none found" style value links to a search log that exists', () => {
    open('research')
    for (const s of values.schools) expect(existsSync(`${ROOT}data/sources/${s.slug}/search-log.md`)).toBe(true)
    const absences = values.schools.flatMap((s) => Object.values(s.values)).filter((v) => !v.quote).length
    expect(screen.getAllByRole('link', { name: 'Search log' })).toHaveLength(absences)
  })

  test('a text fragment matches the whole quote (never first,last words), escapes dashes, skips PDFs', () => {
    const q = 'You may not use code or text produced by advanced code-authoring tools, e.g. ChatGPT.'
    expect(quoteLink('https://x.edu/p', q)).toBe(
      'https://x.edu/p#:~:text=You%20may%20not%20use%20code%20or%20text%20produced%20by%20advanced%20code%2Dauthoring%20tools%2C%20e.g.%20ChatGPT',
    )
    expect(quoteLink('https://x.edu/p', 'short self-check')).toBe('https://x.edu/p#:~:text=short%20self%2Dcheck')
    expect(quoteLink('https://x.edu/a.pdf', q, 'data/sources/x/a.pdf')).toBeNull()
  })

  test('the group filter shows only that sample', () => {
    open('research')
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'Ohio' } })
    const names = [...document.querySelectorAll('.school-name')].map((n) => n.textContent)
    expect(names).toEqual(SCHOOLS.filter((s) => s.group === 'Ohio').map((s) => s.name))
  })
})

describe('Validation', () => {
  const files = readdirSync(ROOT + 'validation/runs').filter((f) => f.endsWith('.json'))

  test('lists exactly one entry per file in validation/runs', () => {
    open('validation')
    expect(screen.getAllByTestId('run')).toHaveLength(files.length)
    expect(RUNS.map((r) => r.file).sort()).toEqual(files.sort())
  })

  test('"had failures" shows only runs with failed tests, and each is under Errors caught', () => {
    open('validation')
    fireEvent.change(select('Status'), { target: { value: 'failed' } })
    const shown = screen.getAllByTestId('run')
    const failing = files.filter((f) => readJson('validation/runs/' + f).summary.failed > 0)
    expect(shown).toHaveLength(failing.length)
    for (const r of shown) expect(r.textContent).toMatch(/\d+ failed/)
    expect(within(screen.getByRole('list', { name: 'Errors caught' })).getAllByRole('listitem')).toHaveLength(
      failing.length,
    )
  })

  test('phase and suite filters show only matching runs', () => {
    expect(filterRuns(RUNS, { phase: '0' }).every((r) => r.phase === '0')).toBe(true)
    expect(filterRuns(RUNS, { suite: 'study' }).map((r) => r.file)).toEqual(
      RUNS.filter((r) => r.file.endsWith('_study.json')).map((r) => r.file),
    )
  })

  test('searching a test name finds the runs that contain it', () => {
    open('validation')
    fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'test_s2' } })
    const shown = screen.getAllByTestId('run')
    expect(shown.length).toBeGreaterThan(0)
    for (const r of shown) expect(r.textContent).toMatch(/study/)
  })

  test('the study check table has all 15 schools, each cell matching checks.json', () => {
    open('validation')
    const studyChecks = readJson('data/coded/checks.json')
    const rows = within(screen.getByRole('table', { name: 'Study checks per school' })).getAllByRole('row')
    expect(rows).toHaveLength(16)
    const ids = [...rows[0].querySelectorAll('th')].slice(1).map((th) => th.textContent)
    expect(ids).toEqual(['S1', 'S2', 'S3', 'S4', 'S5', 'C1', 'C2', 'C3', 'C4', 'N1'])
    studyChecks.schools.forEach((s, i) => {
      const cells = [...rows[i + 1].querySelectorAll('td')].map((td) => td.textContent)
      expect(cells).toEqual(ids.map((id) => (s.checks[id] === undefined ? 'n/a' : s.checks[id] ? 'pass' : 'FAIL')))
    })
  })
})

describe('Contributions', () => {
  const entries = contributions.entries

  test('with no filters, every entry is shown (replies under their prompts)', () => {
    open('contributions')
    const replies = entries.filter((e) => e.kind === 'reply')
    expect(screen.getAllByTestId('entry')).toHaveLength(entries.length - replies.length)
    expect(document.querySelectorAll('details.reply')).toHaveLength(replies.length)
  })

  test('every prompt has its reply reachable from it', () => {
    const prompts = entries.filter((e) => e.kind === 'prompt' && e.text !== '[hidden by Marcus]')
    for (const p of prompts) expect(entries.some((e) => e.kind === 'reply' && e.turn === p.turn)).toBe(true)
  })

  test('filtering by person shows only that person', () => {
    open('contributions')
    fireEvent.change(select('Who'), { target: { value: 'Marcus' } })
    const marcus = screen.getAllByTestId('entry')
    expect(marcus.every((e) => e.dataset.actor === 'Marcus')).toBe(true)
    expect(marcus).toHaveLength(entries.filter((e) => e.actor.startsWith('Marcus')).length)
    fireEvent.change(select('Who'), { target: { value: 'Claude' } })
    const claude = screen.getAllByTestId('entry')
    expect(claude.every((e) => e.dataset.actor === 'Claude')).toBe(true)
    expect(claude).toHaveLength(entries.filter((e) => !e.actor.startsWith('Marcus')).length)
  })

  test('every entry has a phase', () => {
    expect(entries.filter((e) => !e.phase)).toEqual([])
  })
})

describe('Token usage', () => {
  const classes = ['input', 'cacheWrite', 'cacheRead', 'output']

  test('the four totals equal the sum of the per-response rows and are shown separately', () => {
    open('tokens')
    const table = screen.getByRole('table', { name: 'Token totals' })
    for (const c of classes) {
      const sum = tokens.responses.reduce((n, r) => n + r[c], 0)
      expect(tokens.totals[c]).toBe(sum)
      expect(table.querySelector(`[data-class="${c}"]`).textContent).toBe(sum.toLocaleString('en-US'))
    }
  })

  test('the phase rows add up to the totals', () => {
    for (const c of [...classes, 'responses']) {
      const sum = Object.values(tokens.byPhase).reduce((n, r) => n + r[c], 0)
      expect(sum).toBe(tokens.totals[c])
    }
  })

  test('the reset table has at least one /clear and one /compact row', () => {
    open('tokens')
    const rows = within(screen.getByRole('table', { name: 'Context resets' })).getAllByRole('rowheader')
    const kinds = rows.map((r) => r.textContent)
    expect(kinds).toContain('/clear')
    expect(kinds).toContain('/compact')
    expect(kinds.filter((k) => k === '/compact')).toHaveLength(tokens.resets.length)
  })

  test('every usage reading is in the readings table', () => {
    open('tokens')
    const rows = within(screen.getByRole('table', { name: 'Plan-limit readings' })).getAllByRole('row')
    expect(rows).toHaveLength(tokens.readings.length + 1)
  })
})
