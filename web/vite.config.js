/// <reference types="vitest/config" />
// Vitest reads this file too when there is no vitest.config, so test settings live here
// (reference/vitest-v5.1.0/docs/config/index.md).
import react from '@vitejs/plugin-react'
import { execSync } from 'node:child_process'
import { defineConfig } from 'vite'
import { configDefaults } from 'vitest/config'

// The commit this build came from. The page footer shows it so anyone can check that the live
// site matches the repository. GitHub Actions provides GITHUB_SHA; locally we ask git.
function buildCommit() {
  if (process.env.GITHUB_SHA) return process.env.GITHUB_SHA.slice(0, 7)
  try {
    return execSync('git rev-parse --short HEAD', { stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim()
  } catch {
    return 'uncommitted'
  }
}

export default defineConfig({
  // Served from https://marcus-hollimon.github.io/Project-2-AI-Use-In-Schools/
  // (reference/vite-v8.3.6/docs/guide/static-deploy.md, "GitHub Pages", step 1).
  base: '/Project-2-AI-Use-In-Schools/',
  plugins: [react()],
  define: {
    __BUILD_COMMIT__: JSON.stringify(buildCommit()),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  test: {
    environment: 'jsdom',
    // Print results as usual, and also write them as JSON for scripts/record-tests.mjs to save.
    reporters: [...configDefaults.reporters, 'json'],
    outputFile: { json: './test-results/vitest.json' },
  },
})
