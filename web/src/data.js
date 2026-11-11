// Every number and quote on the site comes from these repository files, read at build time.
// Nothing here is typed in by hand: change a file, rebuild, and the pages change with it.
import codebook from '../../study/codebook.json'
import values from '../../data/coded/values.json'
import studyChecks from '../../data/coded/checks.json'
import refetch from '../../data/coded/refetch-report.json'
import sampleCsv from '../../data/frame/sample.csv?raw'
import contributions from '../../data/derived/contributions.json'
import tokens from '../../data/derived/tokens.json'
import pipelineChecks from '../../data/derived/checks.json'
import claimsFile from '../../validation/claims.json'
import caughtFile from '../../validation/caught.json'
import { REPO_URL } from './routes.js'

export { codebook, values, studyChecks, refetch, contributions, tokens, pipelineChecks }

// The claims register (Phase 4): every factual sentence on the site and what backs it.
export const CLAIMS = claimsFile.claims
export const CAUGHT = caughtFile.entries
// Pipeline check C5, one result per (claim, test); empty until build.py has run with the register.
export const CLAIM_RESULTS = pipelineChecks.C5_claims ?? []
// Pipeline check C6: each mutation run failed and a later run of its suite passed.
export const MUTATION_RESULTS = pipelineChecks.C6_mutations ?? []
export const TEST_COMMANDS = pipelineChecks.testCommands ?? { recorded: 0, unrecorded: 0 }

// Every recorded test run (validation/runs/*.json), keyed by file path.
const runModules = import.meta.glob('../../validation/runs/*.json', { eager: true, import: 'default' })

export const repoFile = (path) => `${REPO_URL}/blob/main/${path}`

const TZ = 'America/New_York'
export function eastern(iso, opts = { dateStyle: 'medium', timeStyle: 'short' }) {
  return new Intl.DateTimeFormat('en-US', { timeZone: TZ, ...opts }).format(new Date(iso))
}
export const easternDay = (iso) => eastern(iso, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
export const easternTime = (iso) => eastern(iso, { hour: 'numeric', minute: '2-digit' })
export const fmt = (n) => (n == null ? '' : Number(n).toLocaleString('en-US'))

// ---------- Research findings ----------

export const STRATA = [
  { id: 'S1', label: 'Public R1 universities' },
  { id: 'S2', label: 'Private nonprofit R1 universities' },
  { id: 'S3', label: 'Other four-year schools awarding many graduate degrees' },
  { id: 'S4', label: "Four-year schools awarding mostly bachelor's degrees" },
  { id: 'S5', label: "Schools awarding mostly associate's degrees" },
]

export const VARIABLES = [
  { id: 'univ_stance', label: 'University stance on student AI use' },
  { id: 'dept_stance', label: 'CS department stance on student AI use' },
  { id: 'univ_tone', label: 'Tone of university publications' },
  { id: 'dept_tone', label: 'Tone of CS department publications' },
  { id: 'collaboration', label: 'Discusses collaborating with AI' },
  { id: 'disclosure', label: 'Disclosure of AI use' },
  { id: 'se_courses', label: 'Software engineering course policy' },
]

export function allowedValues(variable) {
  const v = codebook.variables[variable]
  return Object.keys((v.same_values_as ? codebook.variables[v.same_values_as] : v).values)
}

export const isAbsence = (value) => codebook.absence_values.includes(value)

function parseCsv(text) {
  const [head, ...rows] = text.trim().split(/\r?\n/)
  const keys = head.split(',')
  return rows.map((line) => Object.fromEntries(line.split(',').map((c, i) => [keys[i], c])))
}

// Every school in the sample: coded values joined to their group and stratum, and whether they passed the checks.
export const SCHOOLS = (() => {
  const frame = Object.fromEntries(parseCsv(sampleCsv).map((r) => [r.unitid, r]))
  const passed = Object.fromEntries(studyChecks.schools.map((s) => [s.unitid, s.pass]))
  return values.schools.map((s) => ({
    ...s,
    group: frame[s.unitid].group === 'ohio' ? 'Ohio' : 'National',
    stratum: frame[s.unitid].stratum,
    how: frame[s.unitid].how,
    passedChecks: passed[s.unitid],
  }))
})()

// counts[value][column] where column is S1..S5, 'national' or 'ohio'. Ohio is never in S1..S5
// or 'national': it is a separate sample.
export function countTable(variable, schools = SCHOOLS) {
  const counts = Object.fromEntries(allowedValues(variable).map((v) => [v, { national: 0, ohio: 0 }]))
  for (const s of schools) {
    const row = counts[s.values[variable].value]
    if (s.group === 'Ohio') row.ohio += 1
    else {
      row.national += 1
      row[s.stratum] = (row[s.stratum] ?? 0) + 1
    }
  }
  return counts
}

// "What the data shows": short sentences computed from values.json and sample.csv. Counts only, never
// percentages (the groups are small), and the Ohio sample is always counted apart from the national one.
export function findings(schools = SCHOOLS) {
  const size = (group) => schools.filter((s) => s.group === group).length
  const n = (group, variable, value) =>
    schools.filter((s) => s.group === group && s.values[variable].value === value).length
  const stances = (group) => {
    const key = group === 'Ohio' ? 'ohio' : 'national'
    return Object.entries(countTable('univ_stance', schools))
      .filter(([, row]) => row[key] > 0)
      .sort((a, b) => b[1][key] - a[1][key])
      .map(([value, row]) => `${value} ${row[key]}`)
      .join(', ')
  }
  const [N, O] = [size('National'), size('Ohio')]
  return [
    {
      id: 'research-finding-dept',
      text: `${n('National', 'dept_stance', 'none found')} of ${N} national computer science departments and ${n('Ohio', 'dept_stance', 'none found')} of ${O} in Ohio had no AI statement of their own that could be found.`,
    },
    {
      id: 'research-finding-stance',
      text: `University stances, national (of ${N}): ${stances('National')}. Ohio (of ${O}): ${stances('Ohio')}.`,
    },
    {
      id: 'research-finding-disclosure',
      text: `Official text requires students to disclose their AI use at ${n('National', 'disclosure', 'required')} of ${N} national schools and ${n('Ohio', 'disclosure', 'required')} of ${O} in Ohio.`,
    },
    {
      id: 'research-finding-syllabus',
      text: `No public software engineering syllabus could be found for ${n('National', 'se_courses', 'no public syllabus found')} of ${N} national schools and ${n('Ohio', 'se_courses', 'no public syllabus found')} of ${O} in Ohio.`,
    },
  ]
}

const FILE_ARCHIVE = /\.(pdf|docx?)$/i

// A link that opens the live page scrolled to the quote and highlighted (a "text fragment").
// Browsers without support open the page at the top. Only for web pages: PDF and Word files open
// in viewers that do not read text fragments.
// The whole quote is matched, never "first words,last words": on 2026-11-11 the short form for an
// MIT quote matched an earlier sentence that also began "You may not use" and highlighted a whole
// page section. A whole-quote link either lands on the exact sentence or opens the page at the top.
export function quoteLink(url, quote, archive = '') {
  if (FILE_ARCHIVE.test(archive) || FILE_ARCHIVE.test(url)) return null
  const text = quote.replace(/\s+/g, ' ').trim().replace(/^[\s"'“‘….]+/, '').replace(/[\s"'”’….,;:]+$/, '')
  // Commas, ampersands and dashes have meaning inside a text fragment, so they are always escaped.
  const directive = encodeURIComponent(text).replace(/-/g, '%2D')
  return `${url}${url.includes('#') ? '' : '#'}:~:text=${directive}`
}

export const searchLogPath = (slug) => `data/sources/${slug}/search-log.md`

// ---------- Validation ----------

export const RUNS = Object.entries(runModules)
  .map(([path, r]) => ({
    file: path.split('/').pop(),
    suite: r.suite,
    phase: String(r.phase),
    label: r.label ?? '',
    startedAt: r.startedAt,
    gitCommit: r.gitCommit,
    uncommittedChanges: r.uncommittedChanges,
    command: r.command,
    correction: r.correction ?? null,
    summary: r.summary,
    tests: (r.report?.testResults ?? []).flatMap((f) =>
      (f.assertionResults ?? []).map((a) => ({
        name: a.fullName,
        status: a.status,
        failureMessages: a.failureMessages ?? [],
      })),
    ),
  }))
  .sort((a, b) => b.startedAt.localeCompare(a.startedAt))

export function filterRuns(runs, { phase = 'all', suite = 'all', status = 'all', query = '' } = {}) {
  const q = query.trim().toLowerCase()
  return runs.filter(
    (r) =>
      (phase === 'all' || r.phase === phase) &&
      (suite === 'all' || r.suite === suite) &&
      (status === 'all' || (status === 'failed') === r.summary.failed > 0) &&
      (!q || r.label.toLowerCase().includes(q) || r.tests.some((t) => t.name.toLowerCase().includes(q))),
  )
}

export const STUDY_CHECKS = [
  ['S1', 'Every quote is found word for word in the saved copy of its page.'],
  ['S2', 'Every saved copy still matches the fingerprint (SHA-256) taken when it was saved.'],
  ['S3', 'Every saved copy has a fetch record: address, time, HTTP status.'],
  ['S4', 'Every source is on the school’s own website.'],
  ['S5', `Quotes are short (${codebook.max_quote_words} words or fewer).`],
  ['C1', 'Every value and source type is one the codebook allows.'],
  ['C2', 'Values are consistent: a coded value has a quote, an address and a saved copy; a “none found” value lists the pages reviewed or a search log; stance and tone agree on “none found”.'],
  ['C3', 'Every quote contains a cue word the codebook lists for its value.'],
  ['C4', 'The required searches for the school are logged, with what each one returned.'],
  ['N1', 'Before a stance or tone is coded “none found”, the second set of searches is logged with results.'],
]
// A school with no quotes has nothing for S1 to S5 or C3 to check, and one with no "none found"
// stance or tone has nothing for N1: those cells show "n/a", never a pass or a fail.

// ---------- Contributions ----------

export const isMarcus = (actor) => actor.startsWith('Marcus')

// ---------- Token usage ----------

export const CLASS_LABELS = {
  input: 'Input (new, uncached)',
  cacheWrite: 'Cache write',
  cacheRead: 'Cache read',
  output: 'Output (includes thinking)',
}

const PHASE_ORDER = ['planning', '0', '1', '2', '3', '4', '5', '6']
export const phaseRows = () =>
  Object.entries(tokens.byPhase).sort((a, b) => PHASE_ORDER.indexOf(a[0]) - PHASE_ORDER.indexOf(b[0]))

// Every context reset, from the usage readings either side of it. A reading whose "reset before
// this" column starts with /compact or /clear is the first reading after that reset; the reading
// before it is the last one before. For a /compact the transcript's own token counts are added.
export function resetRows() {
  const readings = tokens.readings
  const rows = []
  readings.forEach((r, i) => {
    const kind = r.reset.startsWith('/compact') ? '/compact' : r.reset.startsWith('/clear') ? '/clear' : null
    if (!kind) return
    const before = [...readings.slice(0, i)].reverse().find((x) => x.context != null)
    const boundary =
      kind === '/compact'
        ? tokens.resets.find((b) => b.time > before.time && b.time <= r.time)
        : null
    rows.push({
      kind,
      before,
      after: r,
      transcriptBefore: boundary?.preTokens ?? null,
      transcriptAfter: boundary?.postTokens ?? null,
      time: boundary?.time ?? r.time, // the /compact itself; for a /clear, its first reading after
      // A reading taken for the reset says "just before" in its moment; otherwise none was taken.
      noReadingJustBefore: !/just before/.test(before.moment),
    })
  })
  return rows
}
