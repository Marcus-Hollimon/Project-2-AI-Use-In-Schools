// Builds presentation/AI-in-CS-departments.pptx from the repository's data files (Phase 6,
// specs/phase-6-evaluation.md, Part B).
//
// Every number on a slide is read from a file here, never typed in. A title that states a finding is
// checked against the data first, and the build stops with an error if the data no longer supports it.
// The two slides for Marcus's evaluation and reflection carry his headings only.
//
// Run from presentation/:  npm install   (once)   then   npm run build
const fs = require('fs')
const path = require('path')
const PptxGenJS = require('pptxgenjs')
const JSZip = require('jszip') // installed with pptxgenjs

const ROOT = path.resolve(__dirname, '..')
const OUT = path.join(__dirname, 'AI-in-CS-departments.pptx')
const SITE = 'https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/'
const REPO = 'https://github.com/Marcus-Hollimon/Project-2-AI-Use-In-Schools' // web/src/routes.js

// ---------- Data (all from repository files) ----------
const readJson = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf-8'))
const listDir = (p) => fs.readdirSync(path.join(ROOT, p))
function check(ok, message) {
  if (!ok) throw new Error('The data no longer supports a slide: ' + message)
}

const csv = fs.readFileSync(path.join(ROOT, 'data/frame/sample.csv'), 'utf-8').trim().split(/\r?\n/)
const head = csv[0].split(',')
const frame = Object.fromEntries(
  csv.slice(1).map((line) => {
    const r = Object.fromEntries(line.split(',').map((c, i) => [head[i], c]))
    return [r.unitid, r]
  }),
)
const schools = readJson('data/coded/values.json').schools.map((s) => ({
  ...s,
  group: frame[s.unitid].group === 'ohio' ? 'Ohio' : 'National',
  stratum: frame[s.unitid].stratum,
  how: frame[s.unitid].how,
}))
const inGroup = (g) => schools.filter((s) => s.group === g)
const N = inGroup('National').length
const O = inGroup('Ohio').length
const count = (g, variable, value) => inGroup(g).filter((s) => s.values[variable].value === value).length
// [value, count] pairs for one variable in one group, most common first (ties keep codebook order).
const codebook = readJson('study/codebook.json')
function tally(g, variable) {
  const spec = codebook.variables[variable]
  const values = Object.keys((spec.same_values_as ? codebook.variables[spec.same_values_as] : spec).values)
  return values.map((v) => [v, count(g, variable, v)]).filter(([, n]) => n > 0).sort((a, b) => b[1] - a[1])
}
// Codebook v3 rule (d): a "required" disclosure read from a plagiarism or cheating rule has a cue_reason.
const required = (g, fromRule) =>
  inGroup(g).filter((s) => s.values.disclosure.value === 'required' && Boolean(s.values.disclosure.cue_reason) === fromRule).length

const STRATA = [ // labels as in web/src/data.js
  ['S1', 'Public R1 universities'],
  ['S2', 'Private nonprofit R1 universities'],
  ['S3', 'Other four-year schools awarding many graduate degrees'],
  ['S4', "Four-year schools awarding mostly bachelor's degrees"],
  ['S5', "Schools awarding mostly associate's degrees"],
]
const perStratum = STRATA.map(([id]) => inGroup('National').filter((s) => s.stratum === id).length)
const chosenOhio = inGroup('Ohio').filter((s) => s.how === 'fixed by Marcus').length

const savedCopies = fs
  .readdirSync(path.join(ROOT, 'data/sources'))
  .flatMap((d) => (fs.statSync(path.join(ROOT, 'data/sources', d)).isDirectory() ? listDir('data/sources/' + d) : []))
  .filter((f) => f.endsWith('.meta.json')).length
const quotes = schools.reduce((n, s) => n + Object.values(s.values).filter((v) => v.quote).length, 0)
const studyChecks = readJson('data/coded/checks.json')
const schoolsPassing = studyChecks.schools.filter((s) => s.pass).length
const CHECK_COUNT = 10 // S1 to S5, C1 to C4, N1 (study/check_study.py CHECKS)
check(studyChecks.schools.every((s) => Object.keys(s.checks).length <= CHECK_COUNT), 'more than 10 study checks')

const runFiles = listDir('validation/runs').filter((f) => f.endsWith('.json')).sort()
const runs = runFiles.map((f) => readJson('validation/runs/' + f))
const newest = (suite) => runs.filter((r) => r.suite === suite).at(-1)
const handMutations = runs.filter((r) => r.summary.failed > 0 && /^mutation/i.test(r.label ?? '')).length
const mutationRuns = listDir('validation/mutation-runs').filter((f) => f.endsWith('.json')).sort()
const firstMutation = readJson('validation/mutation-runs/' + mutationRuns[0])
const lastMutation = readJson('validation/mutation-runs/' + mutationRuns.at(-1))
const triage = readJson('validation/mutation-triage.json').entries
const claims = readJson('validation/claims.json').claims.length
const caught = readJson('validation/caught.json').entries.length

const contributions = readJson('data/derived/contributions.json').entries
const by = (kind, actor) => contributions.filter((e) => e.kind === kind && e.actor.startsWith(actor)).length
const tokens = readJson('data/derived/tokens.json')
const totalTokens = tokens.classes.reduce((n, c) => n + tokens.totals[c], 0)
const compacts = tokens.resets.length
const clears = tokens.readings.filter((r) => r.reset.startsWith('/clear')).length
const refetch = readJson('data/coded/refetch-report.json')
const refetchQuotes = refetch.rows.flatMap((r) => r.quotes ?? []).length
const refetchDay = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', month: 'long', day: 'numeric' }).format(new Date(refetch.generated_at))
const specs = listDir('specs').filter((f) => /^phase-\d+-.*\.md$/.test(f)).length

const fmt = (n) => Number(n).toLocaleString('en-US')
const millions = (n) => (n / 1e6).toFixed(1) + ' million'

// ---------- Design ----------
const P = {
  ink: '1E2A30', inkSoft: '33444C', paper: 'FFFFFF', panel: 'F1F4F3', line: 'D3DBD9',
  text: '1E2A30', muted: '56666B', onInk: 'D7E0DE',
  amber: 'F2B134', amberSoft: 'FCE6B6', teal: '1D746C', tealSoft: 'B5D9D3',
  ohio: 'A82E3D', ohioSoft: 'EBC0C5', grey: 'CDD4D2', white: 'FFFFFF',
}
const THEME = {
  name: 'Highlighter',
  colors: {
    dk1: P.ink, lt1: P.paper, dk2: P.inkSoft, lt2: P.panel, accent1: P.teal, accent2: P.amber, accent3: P.ohio,
    accent4: P.muted, accent5: P.tealSoft, accent6: P.amberSoft, hlink: P.teal, folHlink: P.inkSoft,
  },
}
const HEAD = 'Cambria'
const BODY = 'Calibri'
const CHART_FONT = '+mn-lt' // the theme's body font, for chart text

const pres = new PptxGenJS()
pres.layout = 'LAYOUT_16x9' // 10 x 5.625 inches
pres.author = 'Marcus Hollimon'
pres.title = 'How US computer science departments talk about generative AI'
pres.subject = 'Project 2 final presentation'
pres.theme = { headFontFace: HEAD, bodyFontFace: BODY }

pres.defineSlideMaster({
  title: 'DARK',
  background: { color: P.ink },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.7, w: 8.8, h: 2.1, fontFace: HEAD, fontSize: 38, bold: true, color: P.white, align: 'left', valign: 'bottom', margin: 0 }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.6, y: 3.0, w: 8.8, h: 1.0, fontFace: BODY, fontSize: 18, color: P.onInk, align: 'left', valign: 'top', margin: 0 }, text: '' } },
  ],
})
pres.defineSlideMaster({
  title: 'DARK_TOP',
  background: { color: P.ink },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.6, y: 0.3, w: 8.8, h: 0.75, fontFace: HEAD, fontSize: 32, bold: true, color: P.white, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
  ],
})
pres.defineSlideMaster({
  title: 'CONTENT',
  background: { color: P.paper },
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontFace: BODY, fontSize: 10, color: P.muted, align: 'right' },
  objects: [
    { text: { text: 'How US CS departments talk about generative AI · Marcus Hollimon', options: { x: 0.5, y: 5.2, w: 6.5, h: 0.25, fontFace: BODY, fontSize: 10, color: P.muted, margin: 0 } } },
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontFace: HEAD, fontSize: 32, bold: true, color: P.ink, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
  ],
})
pres.defineSlideMaster({
  title: 'MARCUS',
  background: { color: P.panel },
  slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.25, fontFace: BODY, fontSize: 10, color: P.muted, align: 'right' },
  objects: [
    { placeholder: { options: { name: 'title', type: 'title', x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontFace: HEAD, fontSize: 32, bold: true, color: P.ink, align: 'left', valign: 'middle', margin: 0 }, text: '' } },
    { placeholder: { options: { name: 'body', type: 'body', x: 0.5, y: 1.3, w: 9.0, h: 3.7, fontFace: BODY, fontSize: 18, color: P.text, valign: 'top', margin: 0 }, text: '' } },
  ],
})

// ---------- Helpers ----------
function text(slide, value, opts) {
  slide.addText(value, { isTextBox: true, margin: 0, fontFace: BODY, color: P.text, fontSize: 14, valign: 'top', ...opts })
}
// The motif: a number or phrase marked with an amber highlighter, as the site marks a quote on the live page.
function marked(value, opts = {}) {
  return { text: value, options: { highlight: P.amber, bold: true, ...opts } }
}
function card(slide, x, y, w, h, fill = P.panel, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: name })
}
// A row of dots, one per school, colored by group: [{ n, color }].
function dots(slide, x, y, groups, { size = 0.2, gap = 0.08, perRow = 10, name = 'dots' } = {}) {
  let i = 0
  for (const g of groups) {
    for (let k = 0; k < g.n; k++, i++) {
      const col = i % perRow
      const row = Math.floor(i / perRow)
      slide.addShape(pres.shapes.OVAL, {
        x: x + col * (size + gap), y: y + row * (size + gap), w: size, h: size,
        fill: { color: g.color }, line: { color: g.color }, objectName: `${name} ${i + 1}`,
      })
    }
  }
}
function barChart(slide, x, y, w, h, title, pairs, color) {
  slide.addChart(pres.charts.BAR, [{ name: title, labels: pairs.map(([v]) => v), values: pairs.map(([, n]) => n) }], {
    x, y, w, h, barDir: 'bar', chartColors: [color], barGapWidthPct: 55,
    showTitle: true, title, titleFontSize: 14, titleColor: P.ink, titleFontFace: CHART_FONT,
    showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: P.text, dataLabelFontSize: 13, dataLabelFontFace: CHART_FONT,
    catAxisLabelColor: P.text, catAxisLabelFontSize: 12, catAxisLabelFontFace: CHART_FONT, catAxisOrientation: 'maxMin',
    catAxisLineShow: false, valAxisHidden: true, valAxisLineShow: false, valAxisMaxVal: Math.max(...pairs.map(([, n]) => n)) + 2,
    valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, showLegend: false,
  })
}
function slideOf(master, section) {
  return pres.addSlide({ masterName: master, sectionTitle: section })
}

// ---------- Slides ----------
// 1. Title
pres.addSection({ title: 'Opening' })
{
  const s = slideOf('DARK', 'Opening')
  s.addText([
    { text: 'How US computer science', options: { breakLine: true } },
    { text: 'departments talk about', options: { breakLine: true } },
    { text: 'generative AI', options: { color: P.amber } },
  ], { placeholder: 'title' })
  s.addText(`A small study of ${schools.length} schools, built with Claude Code and checked by automated tests`, { placeholder: 'body' })
  text(s, `Marcus Hollimon · Project 2 · November 2026`, { x: 0.6, y: 4.45, w: 8.8, h: 0.3, fontSize: 14, color: P.onInk })
  text(s, SITE, { x: 0.6, y: 4.8, w: 8.8, h: 0.3, fontSize: 12, color: P.amber, hyperlink: { url: SITE } })
  s.addNotes(
    `This project had two goals. The first is a small research study: how computer science departments at US colleges talk about generative AI in their official pages. The second is to show a way of building software where an AI agent, Claude Code, writes the code while I set the rules and check the results through written specs and automated tests. Everything I show today is on the website, with a link to the exact sentence each answer came from.`,
  )
}

// 2. The questions
{
  const s = slideOf('CONTENT', 'Opening')
  s.addText('Three questions', { placeholder: 'title' })
  const qs = [
    ['Stance', 'Do departments permit, encourage or restrict student use of generative AI?'],
    ['Tone', 'Do their official pages take a positive view, and do they talk about working with AI?'],
    ['Courses', 'How do software engineering courses handle it in their syllabi?'],
  ]
  qs.forEach(([label, q], i) => {
    const x = 0.5 + i * 3.08
    card(s, x, 1.3, 2.86, 2.45, P.panel, `question ${i + 1}`)
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.55, w: 0.55, h: 0.55, fill: { color: P.teal }, line: { color: P.teal }, objectName: `number ${i + 1}` })
    text(s, String(i + 1), { x: x + 0.25, y: 1.55, w: 0.55, h: 0.55, align: 'center', valign: 'middle', fontSize: 20, bold: true, color: P.white, fontFace: HEAD })
    text(s, label, { x: x + 0.95, y: 1.55, w: 1.75, h: 0.55, valign: 'middle', fontSize: 18, bold: true, fontFace: HEAD })
    text(s, q, { x: x + 0.25, y: 2.3, w: 2.4, h: 1.35, fontSize: 15 })
  })
  text(s, [
    { text: 'And a second goal: ', options: { bold: true } },
    { text: 'show agentic, spec-driven development. Claude Code wrote all the code; I set the rules through specs, tests and reviews, and made every judgment call.' },
  ], { x: 0.5, y: 4.0, w: 9.0, h: 0.9, fontSize: 15, valign: 'middle' })
  s.addNotes(
    `These are the assignment's three questions. Stance asks what students are allowed to do. Tone asks whether the pages sound positive, neutral or cautious, and whether they describe working with AI as a partner. Courses asks what software engineering syllabi say. The second goal is about the process: I did not write code. I wrote and approved specs, decided every judgment call, and the work was checked by tests.`,
  )
}

// 3. The sample
pres.addSection({ title: 'Method' })
{
  const s = slideOf('CONTENT', 'Method')
  s.addText('Who was studied', { placeholder: 'title' })
  check(perStratum.every((n) => n === perStratum[0]), 'strata of unequal size')
  text(s, [{ text: `${N} schools drawn at random, ${perStratum[0]} from each of ${STRATA.length} types`, options: { bold: true } }], { x: 0.5, y: 1.2, w: 5.6, h: 0.35, fontSize: 15 })
  STRATA.forEach(([id, label], i) => {
    const y = 1.7 + i * 0.6
    text(s, id, { x: 0.5, y, w: 0.45, h: 0.3, fontSize: 13, bold: true, color: P.teal, valign: 'middle' })
    dots(s, 0.95, y + 0.03, [{ n: perStratum[i], color: P.teal }], { size: 0.24, gap: 0.07, perRow: 6, name: `${id} school` })
    text(s, label, { x: 2.85, y, w: 3.3, h: 0.3, fontSize: 12, color: P.muted, valign: 'middle' })
  })
  card(s, 6.5, 1.2, 3.0, 3.2, P.panel, 'Ohio sample')
  text(s, [{ text: `${O} Ohio schools`, options: { bold: true } }], { x: 6.75, y: 1.4, w: 2.6, h: 0.35, fontSize: 15, color: P.ohio })
  dots(s, 6.75, 1.9, [{ n: chosenOhio, color: P.ohio }, { n: O - chosenOhio, color: P.ohioSoft }], { size: 0.3, gap: 0.1, perRow: 6, name: 'Ohio school' })
  text(s, `${chosenOhio} chosen by me (Ohio State and Cincinnati), ${O - chosenOhio} at random. Reported on their own, never added into the national counts.`, { x: 6.75, y: 2.45, w: 2.55, h: 1.8, fontSize: 13 })
  text(s, 'Groups this small support counts, not percentages or claims about every US department.', { x: 0.5, y: 4.75, w: 9.0, h: 0.35, fontSize: 13, italic: true, color: P.muted })
  s.addNotes(
    `The national sample is ${N} schools drawn at random from the federal IPEDS list of colleges that awarded computer science degrees in 2024, ${perStratum[0]} from each of five types, from big public research universities to community colleges. Ohio is a separate sample of ${O}: two I chose, Ohio State and Cincinnati, and ${O - chosenOhio} at random. Ohio is always reported separately. Because the groups are small, every finding is a count, such as 10 of 30, never a percentage, and none of it claims to describe all US departments.`,
  )
}

// 4. The coding process
{
  const s = slideOf('CONTENT', 'Method')
  s.addText('How every answer was coded', { placeholder: 'title' })
  const steps = [
    ['Search', `The same ${codebook.required_searches.length} searches at every school, each logged with what it found.`],
    ['Save', `Every page saved the day it was read, with a fingerprint: ${fmt(savedCopies)} saved copies.`],
    ['Quote', `Each of ${Object.keys(codebook.variables).length} questions answered from the codebook, backed by a quote of ${codebook.max_quote_words} words or fewer: ${quotes} quotes.`],
    ['Check', `${CHECK_COUNT} automated checks on every answer: is the quote really on the saved page, is the source the school's own site, does the quote fit the answer?`],
  ]
  steps.forEach(([label, body], i) => {
    const x = 0.5 + i * 2.32
    card(s, x, 1.35, 2.12, 2.75, i === 3 ? P.amberSoft : P.panel, `step ${label}`)
    text(s, `${i + 1}`, { x: x + 0.2, y: 1.5, w: 0.5, h: 0.5, fontSize: 26, bold: true, color: P.teal, fontFace: HEAD })
    text(s, label, { x: x + 0.7, y: 1.55, w: 1.3, h: 0.45, fontSize: 18, bold: true, fontFace: HEAD, valign: 'middle' })
    text(s, body, { x: x + 0.2, y: 2.15, w: 1.75, h: 1.85, fontSize: 13 })
  })
  text(s, [
    { text: 'On the website, every answer links to ' },
    marked('the live page, scrolled to the exact sentence'),
    { text: ', and to the saved copy.' },
  ], { x: 0.5, y: 4.35, w: 9.0, h: 0.5, fontSize: 15, valign: 'middle' })
  s.addNotes(
    `Each school went through the same four steps. First, the same searches, written down with their results, so "none found" means we really looked. Second, every page was saved on the day it was read, with a digital fingerprint that shows it has not been edited since. Third, each of the seven questions got an answer from a fixed list in the codebook, backed by a short quote. Fourth, automated checks run on every answer. On the website, any answer can be opened at the exact sentence on the school's live page.`,
  )
}

// 5. Findings: departments and syllabi
pres.addSection({ title: 'Findings' })
{
  const s = slideOf('CONTENT', 'Findings')
  const dept = [count('National', 'dept_stance', 'none found'), count('Ohio', 'dept_stance', 'none found')]
  const syll = [count('National', 'se_courses', 'no public syllabus found'), count('Ohio', 'se_courses', 'no public syllabus found')]
  check(dept[0] * 2 > N && syll[0] * 2 > N, '"rarely publish": fewer than half the national departments or syllabi are missing')
  s.addText('Departments rarely publish AI rules', { placeholder: 'title' })
  const panel = (x, big, of, ohio, ofOhio, label, name) => {
    card(s, x, 1.3, 4.35, 3.55, P.panel, name)
    text(s, [marked(` ${big} of ${of} `, { fontSize: 44, fontFace: HEAD })], { x: x + 0.3, y: 1.5, w: 3.8, h: 0.9, valign: 'middle' })
    text(s, label, { x: x + 0.3, y: 2.55, w: 3.8, h: 0.9, fontSize: 16 })
    dots(s, x + 0.3, 3.5, [{ n: big, color: P.teal }, { n: of - big, color: P.grey }], { size: 0.16, gap: 0.06, perRow: 15, name: `${name} national` })
    text(s, [{ text: `Ohio: ${ohio} of ${ofOhio}`, options: { bold: true, color: P.ohio } }], { x: x + 0.3, y: 4.15, w: 3.8, h: 0.4, fontSize: 15 })
  }
  panel(0.5, dept[0], N, dept[1], O, 'national CS departments had no AI statement of their own that could be found', 'departments')
  panel(5.15, syll[0], N, syll[1], O, 'national schools had no public software engineering syllabus that could be found', 'syllabi')
  s.addNotes(
    `The clearest finding is how little is public below the university level. At ${dept[0]} of ${N} national schools, and ${dept[1]} of ${O} in Ohio, the computer science department had no AI statement of its own that we could find, so the university's policy was the only official word. And at ${syll[0]} of ${N} national schools and ${syll[1]} of ${O} in Ohio, no software engineering syllabus was public at all, so the third question could only be answered at a handful of schools. Syllabi behind course logins could not be seen by this study.`,
  )
}

// 6. Findings: university stance
{
  const s = slideOf('CONTENT', 'Findings')
  const nat = tally('National', 'univ_stance')
  const ohio = tally('Ohio', 'univ_stance')
  check(nat[0][0] === 'restrict' && nat[0][1] > nat[1][1], '"restrict" is not the single most common national stance')
  s.addText('Restrict is the most common stance', { placeholder: 'title' })
  barChart(s, 0.4, 1.2, 5.4, 3.0, `University stance, national (of ${N})`, nat, P.teal)
  barChart(s, 6.0, 1.2, 3.6, 3.0, `Ohio (of ${O})`, ohio, P.ohio)
  text(s, '"Restrict" is often an integrity rule that forbids AI use without the instructor\'s permission. "Instructor decides" leaves it to each course.', { x: 0.5, y: 4.4, w: 9.0, h: 0.6, fontSize: 14, color: P.muted })
  s.addNotes(
    `This is the university-wide stance on student AI use. Nationally, the most common answer is restrict, at ${nat[0][1]} of ${N} schools, then ${nat.slice(1).map(([v, n]) => `${v} at ${n}`).join(', ')}. "Restrict" is often a line in the academic integrity code saying that AI use without the instructor's permission counts as misconduct, rather than an outright ban. In Ohio: ${ohio.map(([v, n]) => `${v} ${n}`).join(', ')}, of ${O}.`,
  )
}

// 7. Findings: disclosure
{
  const s = slideOf('CONTENT', 'Findings')
  const req = [count('National', 'disclosure', 'required'), count('Ohio', 'disclosure', 'required')]
  const outright = [required('National', false), required('Ohio', false)]
  const fromRule = [required('National', true), required('Ohio', true)]
  check(outright[0] + fromRule[0] === req[0] && outright[1] + fromRule[1] === req[1], 'disclosure split does not add up')
  s.addText(`Disclosure required at ${req[0]} of ${N}`, { placeholder: 'title' })
  text(s, 'Official text requires students to say when they used AI:', { x: 0.5, y: 1.2, w: 9.0, h: 0.35, fontSize: 15 })
  text(s, [{ text: `National (of ${N})`, options: { bold: true, color: P.teal } }], { x: 0.5, y: 1.75, w: 4.6, h: 0.35, fontSize: 15 })
  dots(s, 0.5, 2.2, [{ n: outright[0], color: P.teal }, { n: fromRule[0], color: P.tealSoft }, { n: N - req[0], color: P.grey }], { size: 0.32, gap: 0.1, perRow: 10, name: 'national disclosure' })
  text(s, [{ text: `Ohio (of ${O})`, options: { bold: true, color: P.ohio } }], { x: 5.6, y: 1.75, w: 3.9, h: 0.35, fontSize: 15 })
  dots(s, 5.6, 2.2, [{ n: outright[1], color: P.ohio }, { n: fromRule[1], color: P.ohioSoft }, { n: O - req[1], color: P.grey }], { size: 0.32, gap: 0.1, perRow: 6, name: 'Ohio disclosure' })
  const key = (y, color, label) => {
    s.addShape(pres.shapes.OVAL, { x: 0.5, y: y + 0.06, w: 0.2, h: 0.2, fill: { color }, line: { color }, objectName: 'key ' + label })
    text(s, label, { x: 0.8, y, w: 8.7, h: 0.32, fontSize: 14, valign: 'middle' })
  }
  key(3.65, P.teal, `Stated outright: ${outright[0]} national, ${outright[1]} Ohio`)
  key(4.0, P.tealSoft, `Read from a plagiarism or cheating rule: ${fromRule[0]} national, ${fromRule[1]} Ohio`)
  key(4.35, P.grey, `Encouraged or not stated: ${N - req[0]} national, ${O - req[1]} Ohio`)
  card(s, 5.6, 2.85, 3.9, 1.85, P.amberSoft, 'why the split')
  text(s, [
    { text: 'Why two shades? ', options: { bold: true } },
    { text: 'A plagiarism rule that treats undisclosed AI text as copying implies disclosure without saying it. I asked for those schools to be counted apart from the ones that say it outright.' },
  ], { x: 5.8, y: 2.95, w: 3.5, h: 1.65, fontSize: 13, valign: 'middle' })
  s.addNotes(
    `Disclosure means students must say when and how they used AI. ${req[0]} of ${N} national schools and ${req[1]} of ${O} Ohio schools require it in official text. I asked for this split on the site: at ${outright[0]} national schools the rule is stated outright; at ${fromRule[0]} it comes from a plagiarism or cheating rule that treats undisclosed AI text like copying, which is a reading of the rule rather than its exact words. Both Ohio schools state it outright.`,
  )
}

// 8. Findings: tone and collaboration
{
  const s = slideOf('CONTENT', 'Findings')
  const tone = tally('National', 'univ_tone')
  const toneOhio = tally('Ohio', 'univ_tone')
  check(tone[0][0] === 'neutral' && tone[0][1] > tone[1][1], '"neutral" is not the single most common national tone')
  const collab = Object.fromEntries(tally('National', 'collaboration'))
  // A real example for the notes: an explicit national quote that calls AI a partner.
  const partner = inGroup('National').find((s) => s.values.collaboration.value === 'explicit' && /partner/i.test(s.values.collaboration.quote))
  check(partner, 'no explicit national collaboration quote mentions a partner')
  const partnerWords = partner.values.collaboration.quote.trim()
  s.addText('Neutral is the most common tone', { placeholder: 'title' })
  barChart(s, 0.4, 1.2, 5.2, 3.1, `Tone of university pages, national (of ${N})`, tone, P.teal)
  card(s, 6.0, 1.3, 3.5, 3.0, P.panel, 'collaboration')
  text(s, [{ text: 'Working with AI as a partner', options: { bold: true } }], { x: 6.25, y: 1.45, w: 3.1, h: 0.4, fontSize: 15, fontFace: HEAD })
  text(s, [
    marked(` ${collab.explicit ?? 0} of ${N} `, { fontSize: 28, fontFace: HEAD }),
    { text: '  discuss it explicitly', options: { fontSize: 15, breakLine: true } },
    { text: `${collab['in passing'] ?? 0} mention it in passing, ${collab['not discussed'] ?? 0} not at all.`, options: { fontSize: 14 } },
  ], { x: 6.25, y: 1.95, w: 3.1, h: 1.5 })
  text(s, `Ohio tone: ${toneOhio.map(([v, n]) => `${v} ${n}`).join(', ')} (of ${O}).`, { x: 6.25, y: 3.5, w: 3.1, h: 0.7, fontSize: 13, color: P.ohio })
  text(s, '"Mixed" pages weigh benefits against risks; a rule that names AI only in a list of misconduct reads as neutral.', { x: 0.5, y: 4.45, w: 9.0, h: 0.55, fontSize: 13, color: P.muted })
  s.addNotes(
    `Tone is the overall attitude of the university's pages. Nationally the most common tone is neutral, at ${tone[0][1]} of ${N}: procedural rules with little evaluative language. Then ${tone.slice(1).map(([v, n]) => `${v} ${n}`).join(', ')}. Mixed means a page that weighs benefits against risks. On collaboration, only ${collab.explicit ?? 0} of ${N} national schools explicitly describe students working with AI. ${partner.name}, for example: "${partnerWords}" Another ${collab['in passing'] ?? 0} mention it in passing.`,
  )
}

// 9. Proof: three layers
pres.addSection({ title: 'How we proved it' })
{
  const s = slideOf('CONTENT', 'How we proved it')
  s.addText('Three layers of automated checks', { placeholder: 'title' })
  const study = newest('study')
  const layers = [
    ['The data', `${schoolsPassing} of ${studyChecks.schools.length}`, `schools pass every one of the ${CHECK_COUNT} checks, on every answer`],
    ['The code', `${study.summary.total + newest('pipeline').summary.total}`, `tests of the code that checks and counts (${study.summary.total} study, ${newest('pipeline').summary.total} pipeline)`],
    ['The pages', `${newest('web').summary.total}`, 'tests of what the site shows, recomputing its numbers from the data'],
  ]
  layers.forEach(([label, big, body], i) => {
    const x = 0.5 + i * 3.08
    card(s, x, 1.3, 2.86, 2.4, P.panel, `layer ${label}`)
    text(s, label, { x: x + 0.25, y: 1.45, w: 2.4, h: 0.4, fontSize: 17, bold: true, fontFace: HEAD })
    text(s, [marked(` ${big} `, { fontSize: 36, fontFace: HEAD })], { x: x + 0.25, y: 1.95, w: 2.4, h: 0.75, valign: 'middle' })
    text(s, body, { x: x + 0.25, y: 2.8, w: 2.4, h: 0.85, fontSize: 14 })
  })
  card(s, 0.5, 3.95, 9.0, 0.95, P.amberSoft, 'claims register')
  text(s, [
    { text: `The claims register ties them together: `, options: { bold: true } },
    { text: `all ${claims} factual sentences on the site are listed with the test, file or outside page behind them. A test fails if a sentence is missing from the list.` },
  ], { x: 0.75, y: 4.0, w: 8.5, h: 0.85, fontSize: 14, valign: 'middle' })
  s.addNotes(
    `I am not a programmer, so I could not check the code by reading it. Instead, everything is checked by automated tests in three layers. The data: a checker confirms every quote is word for word on the saved page, the page is the school's own, and the answer fits the codebook; all ${schoolsPassing} schools pass. The code: ${study.summary.total + newest('pipeline').summary.total} tests check the code, most by building a small made-up case that breaks one rule and confirming it is caught. The pages: ${newest('web').summary.total} tests recompute the website's numbers from the data files and compare them with the page. Every test run is saved and searchable on the Validation page.`,
  )
}

// 10. Proof: the tests catch errors
{
  const s = slideOf('CONTENT', 'How we proved it')
  s.addText('We broke things on purpose', { placeholder: 'title' })
  check(triage.length === lastMutation.survived, 'a surviving planted bug has no written verdict')
  // Tests added to close gaps: the newest study run, less the newest study run before the first mutation
  // run, less the tests of the mutation tool itself (the same count as the Validation tab).
  const study = newest('study')
  const studyBefore = runs.filter((r) => r.suite === 'study' && new Date(r.startedAt) < new Date(firstMutation.startedAt)).at(-1)
  const toolTests = study.report.testResults.flatMap((f) => f.assertionResults).filter((a) => a.fullName.includes('test_mutation_score ')).length
  const added = study.summary.total - studyBefore.summary.total - toolTests
  card(s, 0.5, 1.3, 5.0, 3.6, P.panel, 'mutation score')
  text(s, [{ text: 'A tool planted small bugs in the checker, one at a time', options: { bold: true } }], { x: 0.75, y: 1.45, w: 4.5, h: 0.6, fontSize: 15, fontFace: HEAD })
  // Each figure in its own box with its label beside it, so labels never wrap around a number.
  const row = (x, y, big, label, { wBig, wLabel, size, color, mark }) => {
    const run = mark ? marked(` ${big} `, { fontSize: size, fontFace: HEAD }) : { text: big, options: { fontSize: size, bold: true, fontFace: HEAD, color } }
    text(s, [run], { x, y, w: wBig, h: 0.6, valign: 'middle' })
    text(s, label, { x: x + wBig + 0.1, y, w: wLabel, h: 0.6, fontSize: 14, valign: 'middle', color: color ?? P.text })
  }
  row(0.75, 2.15, `${firstMutation.killed} of ${firstMutation.total}`, 'caught at first', { wBig: 2.55, wLabel: 1.85, size: 30, color: P.muted })
  row(0.75, 2.85, `${lastMutation.killed} of ${lastMutation.total}`, `caught after ${added} tests were added`, { wBig: 2.55, wLabel: 1.85, size: 30, mark: true })
  text(s, `The ${lastMutation.survived} left can only change spacing or printout text, never a result; each has a written reason.`, { x: 0.75, y: 3.75, w: 4.5, h: 0.9, fontSize: 13, color: P.muted })
  row(5.8, 1.35, String(handMutations), 'bugs planted by hand, each caught by a test', { wBig: 0.7, wLabel: 2.9, size: 22, mark: true })
  row(5.8, 2.05, String(caught), 'problems found outside test runs, each with a fix and a guard', { wBig: 0.7, wLabel: 2.9, size: 22, mark: true })
  text(s, [
    { text: 'What tests cannot prove', options: { bold: true, breakLine: true } },
    { text: 'That a reading of a page is right: no second coder was used.', options: { bullet: { indent: 14 }, breakLine: true } },
    { text: `Anything about schools outside the ${schools.length}.`, options: { bullet: { indent: 14 }, breakLine: true } },
    { text: 'Pages behind a login.', options: { bullet: { indent: 14 } } },
  ], { x: 5.8, y: 3.15, w: 3.7, h: 1.7, fontSize: 13, paraSpaceAfter: 3 })
  s.addNotes(
    `A test that never fails proves nothing, so the tests were broken on purpose. A mutation tool made ${lastMutation.total} copies of the checker, each with one small bug, like flipping a comparison, and ran the tests on each. The first run caught ${firstMutation.killed}. The misses showed real gaps, for example nobody had tested a quote of exactly ${codebook.max_quote_words} words, the limit. ${added} tests were added, and now ${lastMutation.killed} of ${lastMutation.total} are caught; the ${lastMutation.survived} left cannot change any result, and each has a written reason on the site. I want to be honest about the limit: no set of tests can prove it catches every possible mistake. What the tests cannot check at all is whether a person would read each page the same way, because there was no second coder.`,
  )
}

// 11. Process
pres.addSection({ title: 'Process' })
{
  const s = slideOf('CONTENT', 'Process')
  s.addText('Built phase by phase from specs', { placeholder: 'title' })
  const phases = ['Foundation', 'Instrumentation', 'Study', 'Interfaces', 'Validation', 'More schools', 'Evaluation']
  check(phases.length === specs, `${specs} phase specs, not ${phases.length}`)
  s.addShape(pres.shapes.LINE, { x: 1.15, y: 1.72, w: 7.7, h: 0, line: { color: P.grey, width: 2 }, objectName: 'timeline' })
  phases.forEach((name, i) => {
    const x = 1.15 + i * (7.7 / 6)
    s.addShape(pres.shapes.OVAL, { x: x - 0.17, y: 1.55, w: 0.34, h: 0.34, fill: { color: i === 6 ? P.amber : P.teal }, line: { color: P.white, width: 1.5 }, objectName: `phase ${i}` })
    text(s, String(i), { x: x - 0.17, y: 1.55, w: 0.34, h: 0.34, align: 'center', valign: 'middle', fontSize: 11, bold: true, color: i === 6 ? P.ink : P.white })
    text(s, name, { x: x - 0.65, y: 2.0, w: 1.3, h: 0.5, align: 'center', fontSize: 12 })
  })
  text(s, 'Each phase: a written spec I approved, then the work, then my checklist.', { x: 0.5, y: 1.15, w: 9.0, h: 0.3, fontSize: 14, color: P.muted })
  const stats = [
    [fmt(by('prompt', 'Marcus')), 'prompts from me'],
    [fmt(by('decision', 'Marcus')), 'decisions I made, each logged'],
    [fmt(by('commit', 'Claude')), 'commits by Claude'],
    [`${(totalTokens / 1e6).toFixed(1)}M`, `tokens, ${Math.round((tokens.totals.cacheRead / totalTokens) * 100)}% of them read again from cache`],
  ]
  stats.forEach(([big, label], i) => {
    const x = 0.5 + i * 2.32
    card(s, x, 2.85, 2.12, 1.55, P.panel, `stat ${label}`)
    text(s, [marked(` ${big} `, { fontSize: 24, fontFace: HEAD })], { x: x + 0.2, y: 3.0, w: 1.8, h: 0.6, valign: 'middle' })
    text(s, label, { x: x + 0.2, y: 3.65, w: 1.8, h: 0.65, fontSize: 13 })
  })
  text(s, `Context was reset ${compacts} times with /compact and ${clears} with /clear; the Token usage page compares them.`, { x: 0.5, y: 4.6, w: 9.0, h: 0.4, fontSize: 13, color: P.muted })
  s.addNotes(
    `The work ran in seven phases. Each started with a written spec that I approved, and ended with a checklist I ran myself. Claude asked me whenever a judgment was needed; I made ${by('decision', 'Marcus')} logged decisions, including the judgment calls that became codebook version ${codebook.version}. The Contributions page shows every prompt I wrote and every reply. The Token usage page shows the cost: ${millions(totalTokens)} tokens, most of them the same context re-read from cache on every turn.`,
  )
}

// 12 and 13. Marcus's own slides: his headings only, no text from Claude.
pres.addSection({ title: 'Evaluation and reflection' })
{
  const s = slideOf('MARCUS', 'Evaluation and reflection')
  s.addText('Evaluation against goals', { placeholder: 'title' })
  s.addNotes('For Marcus to write.')
}
{
  const s = slideOf('MARCUS', 'Evaluation and reflection')
  s.addText('Reflection: agentic vs AI-assisted', { placeholder: 'title' })
  s.addNotes('For Marcus to write.')
}

// 14. Limits, next steps, links
pres.addSection({ title: 'Close' })
{
  const s = slideOf('DARK_TOP', 'Close')
  s.addText('Limits and next steps', { placeholder: 'title' })
  const col = (x, title, items) =>
    text(s, [
      { text: title, options: { bold: true, color: P.amber, fontSize: 16, breakLine: true } },
      ...items.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < items.length - 1 } })),
    ], { x, y: 1.2, w: 4.25, h: 2.85, fontSize: 14, color: P.onInk, paraSpaceAfter: 6 })
  col(0.6, 'Limits', [
    `Small groups: ${N} national and ${O} Ohio schools, so counts only.`,
    'One coder; no second person checked the readings.',
    'Public pages only; anything behind a login was out of reach.',
    `Pages change: all ${refetch.pages} were fetched again on ${refetchDay}; ${refetch.coded_quotes_missing_from_new_copy} of the ${refetchQuotes} quotes on changed pages had gone.`,
  ])
  col(5.2, 'Next steps', [
    'A second coder on a sample, to measure agreement.',
    'More schools per type, so groups can be compared.',
    'Re-check the saved pages each term.',
  ])
  text(s, [
    { text: 'Website: ', options: { bold: true } }, { text: SITE, options: { hyperlink: { url: SITE }, color: P.white, breakLine: true } },
    { text: 'Code and data: ', options: { bold: true } }, { text: REPO, options: { hyperlink: { url: REPO }, color: P.white } },
  ], { x: 0.6, y: 4.35, w: 8.8, h: 0.7, fontSize: 13, color: P.onInk })
  s.addNotes(
    `To close, the limits. The groups are small, so these are counts for these schools, not national percentages. I was the only person deciding the readings, so agreement between two coders was not measured; that would be the first thing to add. Only public pages were used. And pages change, so the study saved a copy of every page; when all ${refetch.pages} were fetched again on ${refetchDay}, ${refetch.coded_quotes_missing_from_new_copy} of the ${refetchQuotes} quotes on changed pages had disappeared. Everything is on the website and in the repository, so anyone can check any answer.`,
  )
}

// ---------- Write, then fix what pptxgenjs gets wrong ----------
// pptxgenjs writes Office's color palette into the theme and two small faults PowerPoint offers to
// "repair"; the same fixes as the pptx skill's apply_theme.js, written here so the deck rebuilds from this
// repository alone.
async function finish(file) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file))
  const part = 'ppt/theme/theme1.xml'
  const slots = ['dk1', 'lt1', 'dk2', 'lt2', 'accent1', 'accent2', 'accent3', 'accent4', 'accent5', 'accent6', 'hlink', 'folHlink']
  const scheme = `<a:clrScheme name="${THEME.name}">` + slots.map((k) => `<a:${k}><a:srgbClr val="${THEME.colors[k]}"/></a:${k}>`).join('') + '</a:clrScheme>'
  const theme = (await zip.file(part).async('string'))
    .replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, () => scheme)
    .replace(/(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, (_, h) => `${h}${THEME.name}"`)
  if (!theme.includes(scheme)) throw new Error('no color scheme found in ' + part)
  zip.file(part, theme)
  for (const name of Object.keys(zip.files)) {
    if (!name.endsWith('.xml')) continue
    const xml = await zip.file(name).async('string')
    const bad = xml.match(/<a:srgbClr val="((?![0-9A-Fa-f]{6}")[^"]*)"/)
    if (bad) throw new Error(`${name}: color "${bad[1]}" is not six hex digits`)
    if (xml.includes('<c:crossesAt val="autoZero"/>')) zip.file(name, xml.replaceAll('<c:crossesAt val="autoZero"/>', '<c:crosses val="autoZero"/>'))
  }
  for (const name of Object.keys(zip.files)) if (zip.files[name].dir) delete zip.files[name]
  fs.writeFileSync(file, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }))
}

pres
  .writeFile({ fileName: OUT })
  .then(() => finish(OUT))
  .then(() => console.log(`Wrote ${path.relative(ROOT, OUT)}: ${pres.slides.length} slides`))
  .catch((e) => {
    console.error(e.message)
    process.exit(1)
  })
