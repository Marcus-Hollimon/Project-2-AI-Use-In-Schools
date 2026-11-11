// The site's pages. Navigation uses the part of the address after "#" (for example #/tokens), so
// GitHub Pages always serves the same index.html and a hard refresh can never hit a missing page.
export const REPO_URL = 'https://github.com/Marcus-Hollimon/Project-2-AI-Use-In-Schools'

export const TABS = [
  {
    id: 'overview',
    label: 'Overview',
    deliverable: null,
    title: 'How US computer science departments talk about generative AI',
    summary:
      'A small study of how CS departments permit, encourage, or restrict generative AI, built with agentic development: Claude Code wrote the code, and Marcus supervised through specs, tests, and reviews.',
  },
  {
    id: 'research',
    label: 'Research findings',
    deliverable: 1,
    title: 'Research findings',
    summary:
      'How departments permit or restrict generative AI, whether their official publications view it positively or discuss collaborating with it, and how software engineering courses handle it.',
  },
  {
    id: 'validation',
    label: 'Validation',
    deliverable: 2,
    title: 'Validation evidence',
    summary:
      'Every recorded test run, searchable and filterable, with the errors that tests caught and the study checks for every school.',
  },
  {
    id: 'contributions',
    label: 'Contributions',
    deliverable: 3,
    title: 'Timeline and contributions',
    summary:
      "Who did what and when: Marcus's questions and decisions, Claude's responses and work, all timestamped.",
  },
  {
    id: 'tokens',
    label: 'Token usage',
    deliverable: 4,
    title: 'Token usage',
    summary:
      'Tokens by project phase and by practice (/clear, /compact, new session), deduplicated and split into their four classes.',
  },
]

export const DEFAULT_TAB_ID = 'overview'

export function tabFromHash(hash) {
  const id = String(hash ?? '').replace(/^#\/?/, '')
  return TABS.some((t) => t.id === id) ? id : DEFAULT_TAB_ID
}

export function hashFor(id) {
  return id === DEFAULT_TAB_ID ? '#/' : `#/${id}`
}
