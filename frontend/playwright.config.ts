import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 30_000,
  reporter: [['list'], ['json', { outputFile: process.env.SCENEMIND_E2E_REPORT ?? '../.runtime/test-results/playwright.json' }]],
  use: {
    baseURL: process.env.SCENEMIND_E2E_BASE_URL ?? 'http://127.0.0.1:15173',
    channel: process.env.SCENEMIND_E2E_BROWSER_CHANNEL ?? 'msedge',
    headless: true,
    viewport: { width: 1280, height: 900 },
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  outputDir: process.env.SCENEMIND_E2E_OUTPUT ?? '../.runtime/test-results/playwright-artifacts',
})
