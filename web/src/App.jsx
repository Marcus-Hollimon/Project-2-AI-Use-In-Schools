import { useEffect, useState } from 'react'
import { REPO_URL, TABS, hashFor, tabFromHash } from './routes.js'
import Contributions from './tabs/Contributions.jsx'
import Research from './tabs/Research.jsx'
import Tokens from './tabs/Tokens.jsx'
import Validation from './tabs/Validation.jsx'
import './App.css'

const PAGES = { research: Research, validation: Validation, contributions: Contributions, tokens: Tokens }

// Keeps the visible page in step with the address bar, including Back/Forward and hard refresh.
function useCurrentTabId() {
  const [id, setId] = useState(() => tabFromHash(window.location.hash))
  useEffect(() => {
    const sync = () => setId(tabFromHash(window.location.hash))
    window.addEventListener('hashchange', sync)
    return () => window.removeEventListener('hashchange', sync)
  }, [])
  return id
}

function Overview({ tab }) {
  return (
    <>
      <p className="eyebrow" data-claim="none">Project 2 · Agentic development with Claude Code</p>
      <h1>{tab.title}</h1>
      <p className="lede" data-claim="overview-lede">
        {tab.summary}
      </p>
      <ol className="cards" data-claim="overview-cards">
        {TABS.filter((t) => t.deliverable).map((t) => (
          <li key={t.id}>
            <a className="card" href={hashFor(t.id)}>
              <span className="card-num">Deliverable {t.deliverable}</span>
              <span className="card-title">{t.title}</span>
              <span className="card-body">{t.summary}</span>
              <span className="status">Built from the project’s recorded data</span>
            </a>
          </li>
        ))}
      </ol>
      <p className="note" data-claim="overview-repo">
        Specs, progress logs, and every recorded test run are in the{' '}
        <a href={REPO_URL}>GitHub repository</a>.
      </p>
    </>
  )
}

function Deliverable({ tab }) {
  const Page = PAGES[tab.id]
  return (
    <>
      <p className="eyebrow" data-claim="none">Deliverable {tab.deliverable}</p>
      <h1>{tab.title}</h1>
      <p className="lede" data-claim={`${tab.id}-lede`}>
        {tab.summary}
      </p>
      <Page />
    </>
  )
}

export default function App() {
  const currentId = useCurrentTabId()
  const tab = TABS.find((t) => t.id === currentId)
  const commitUrl =
    __BUILD_COMMIT__ === 'uncommitted' ? REPO_URL : `${REPO_URL}/commit/${__BUILD_COMMIT__}`

  return (
    <div className="shell">
      <header className="top">
        <a className="brand" href={hashFor('overview')}>
          AI in CS Departments
        </a>
        <nav aria-label="Deliverables">
          {TABS.map((t) => (
            <a
              key={t.id}
              href={hashFor(t.id)}
              aria-current={t.id === currentId ? 'page' : undefined}
            >
              {t.deliverable ? `${t.deliverable}. ` : ''}
              {t.label}
            </a>
          ))}
        </nav>
      </header>
      <main>{tab.deliverable ? <Deliverable tab={tab} /> : <Overview tab={tab} />}</main>
      <footer>
        Built from commit{' '}
        <a href={commitUrl}>
          <code>{__BUILD_COMMIT__}</code>
        </a>{' '}
        on {new Date(__BUILD_TIME__).toLocaleString()}.
      </footer>
    </div>
  )
}
