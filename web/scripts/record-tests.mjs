// Runs the web test suite once and saves the full result, with when and which-commit details, to
// validation/runs/. The Validation tab reads those files, so in this project a test result only
// counts if this script recorded it.
import { execSync, spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const webDir = join(dirname(fileURLToPath(import.meta.url)), '..')
const repoDir = join(webDir, '..')
const reportPath = join(webDir, 'test-results', 'vitest.json')
const runsDir = join(repoDir, 'validation', 'runs')

function git(args) {
  try {
    return execSync(`git ${args}`, { cwd: repoDir, stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim()
  } catch {
    return null
  }
}

function currentPhase() {
  try {
    const state = readFileSync(join(repoDir, 'progress', 'STATE.md'), 'utf8')
    const match = state.match(/^Current phase:\s*(\d+)/m)
    return match ? Number(match[1]) : null
  } catch {
    return null
  }
}

rmSync(reportPath, { force: true }) // never mistake an earlier run's report for this one
const startedAt = new Date()
const run = spawnSync('npx', ['vitest', 'run'], { cwd: webDir, stdio: 'inherit', shell: true })
const finishedAt = new Date()

const report = existsSync(reportPath) ? JSON.parse(readFileSync(reportPath, 'utf8')) : null
for (const file of report?.testResults ?? []) {
  file.name = relative(repoDir, file.name).split(sep).join('/')
}

const record = {
  suite: 'web',
  runner: 'vitest',
  command: 'npm run test:record',
  label: process.argv.slice(2).join(' ') || null,
  startedAt: startedAt.toISOString(),
  finishedAt: finishedAt.toISOString(),
  phase: currentPhase(),
  gitCommit: git('rev-parse --short HEAD'),
  uncommittedChanges: (git('status --porcelain') ?? '') !== '',
  exitCode: run.status,
  summary: report
    ? {
        total: report.numTotalTests,
        passed: report.numPassedTests,
        failed: report.numFailedTests,
        skipped: report.numPendingTests + (report.numTodoTests ?? 0),
      }
    : null,
  report,
}

mkdirSync(runsDir, { recursive: true })
const outPath = join(runsDir, `${startedAt.toISOString().replace(/[:.]/g, '-')}_web.json`)
writeFileSync(outPath, JSON.stringify(record, null, 2) + '\n')

const s = record.summary
console.log(`\nRecorded ${relative(repoDir, outPath).split(sep).join('/')}`)
console.log(s ? `${s.passed}/${s.total} passed, ${s.failed} failed` : 'No report: the run crashed.')
console.log(
  `Commit ${record.gitCommit ?? '(none yet)'}${record.uncommittedChanges ? ' plus uncommitted changes' : ''}, phase ${record.phase ?? '?'}`,
)
process.exit(run.status ?? 1)
