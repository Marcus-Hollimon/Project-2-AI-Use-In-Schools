import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, test } from 'vitest'
import App from './App.jsx'
import { DEFAULT_TAB_ID, TABS, hashFor, tabFromHash } from './routes.js'

const deliverableTabs = TABS.filter((t) => t.deliverable)
const pageHeading = () => screen.getByRole('heading', { level: 1 })
const menu = () => screen.getByRole('navigation', { name: 'Deliverables' })

afterEach(() => {
  cleanup()
  window.location.hash = ''
})

describe('tabFromHash: choosing the page from the address', () => {
  test('an empty address shows the overview', () => {
    expect(tabFromHash('')).toBe(DEFAULT_TAB_ID)
    expect(tabFromHash(undefined)).toBe(DEFAULT_TAB_ID)
  })

  test.each(TABS.map((t) => [hashFor(t.id), t.id]))('address %s opens page %s', (hash, id) => {
    expect(tabFromHash(hash)).toBe(id)
  })

  test('an unknown page falls back to the overview instead of breaking', () => {
    expect(tabFromHash('#/no-such-page')).toBe(DEFAULT_TAB_ID)
  })

  test('a missing slash still works (#tokens)', () => {
    expect(tabFromHash('#tokens')).toBe('tokens')
  })
})

describe('App: what a visitor sees', () => {
  test('the overview is shown when no page is chosen', () => {
    render(<App />)
    expect(pageHeading().textContent).toBe(TABS[0].title)
  })

  test.each(deliverableTabs.map((t) => [t.id, t.title]))(
    'opening #/%s directly, as a hard refresh does, shows "%s"',
    (id, title) => {
      window.location.hash = hashFor(id)
      render(<App />)
      expect(pageHeading().textContent).toBe(title)
    },
  )

  test('clicking a menu tab switches the page and marks that tab as current', async () => {
    render(<App />)
    fireEvent.click(within(menu()).getByRole('link', { name: '4. Token usage' }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Token usage' })).toBeTruthy()
    const tab = within(menu()).getByRole('link', { name: '4. Token usage' })
    expect(tab.getAttribute('aria-current')).toBe('page')
  })

  test('the menu lists deliverables 1 to 4 in assignment order', () => {
    render(<App />)
    const labels = within(menu()).getAllByRole('link').map((a) => a.textContent)
    expect(labels).toEqual([
      'Overview',
      '1. Research findings',
      '2. Validation',
      '3. Contributions',
      '4. Token usage',
    ])
  })

  test('the overview links to each deliverable exactly once', () => {
    render(<App />)
    const main = screen.getByRole('main')
    for (const t of deliverableTabs) {
      const links = within(main).getAllByRole('link', {
        name: new RegExp(`^Deliverable ${t.deliverable}(?![0-9])`),
      })
      expect(links).toHaveLength(1)
    }
  })

  test('the footer names the commit the page was built from', () => {
    render(<App />)
    expect(screen.getByRole('contentinfo').textContent).toMatch(/Built from commit \S+/)
  })

  test('the footer no longer calls the site a work in progress (Marcus, end of Phase 6)', () => {
    render(<App />)
    expect(screen.getByRole('contentinfo').textContent).not.toMatch(/work in progress/i)
  })
})
