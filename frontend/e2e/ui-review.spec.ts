import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'

const imagePath = process.env.SCENEMIND_E2E_IMAGE
const apiBase = process.env.SCENEMIND_E2E_API_URL ?? 'http://127.0.0.1:18000/api/v1'
const reviewRoot = process.env.SCENEMIND_UI_REVIEW_DIR ?? '../artifacts/ui-review'
const routes = [
  ['01-home', '/'], ['02-live-lens', '/live'], ['03-analysis', '/analyze'], ['04-memory', '/memory'],
  ['05-agent', '/agent'], ['06-session', '/sessions'], ['07-devices', '/devices'],
  ['08-glasses-simulator', '/glasses'], ['09-insights', '/insights'], ['10-privacy', '/privacy'], ['11-system', '/system'],
] as const
const viewports = [
  { name: 'desktop', width: 1440, height: 900, screenshots: true },
  { name: 'tablet', width: 1024, height: 768, screenshots: false },
  { name: 'mobile', width: 390, height: 844, screenshots: true },
  { name: 'small', width: 360, height: 800, screenshots: false },
]

test.describe.configure({ mode: 'serial' })

for (const viewport of viewports) {
  test(`UI review ${viewport.name} has no horizontal overflow`, async ({ page, request }) => {
    test.setTimeout(90_000)
    if (!imagePath) throw new Error('SCENEMIND_E2E_IMAGE is required')
    await page.setViewportSize({ width: viewport.width, height: viewport.height })

    await page.goto('/analyze')
    await page.locator('input[type=file]').setInputFiles(imagePath)
    await page.locator('.analysis-actions .primary-button').click()
    await expect(page.locator('.success-message')).toBeVisible()
    await request.post(`${apiBase}/capture-sessions`, { data: {
      title: `UI review ${viewport.name}`, source_type: 'evaluation', sample_interval_seconds: 5,
      auto_save_mode: 'manual',
    } })

    for (const [name, route] of routes) {
      await page.goto(route)
      await expect(page.locator('.page-heading, .home-view').first()).toBeVisible()
      if (route === '/agent') {
        await page.locator('#agent-question').fill('Where was my cup last seen?')
        await page.locator('.agent-query button').click()
        await expect(page.locator('.agent-answer-card')).toBeVisible()
      }
      if (route === '/analyze') {
        await page.locator('input[type=file]').setInputFiles(imagePath)
        await page.locator('.analysis-actions .secondary-button').click()
        await expect(page.locator('.object-grid')).toBeVisible()
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(overflow, `${viewport.name} ${route} overflow`).toBeLessThanOrEqual(1)
      if (viewport.screenshots) {
        // Keep keyboard-only affordances out of the review capture while preserving
        // the skip link for real keyboard users.
        await page.locator('#main-content').focus()
        const directory = path.resolve(reviewRoot, viewport.name)
        await mkdir(directory, { recursive: true })
        await page.screenshot({ path: path.join(directory, `${name}.png`), fullPage: true })
      }
    }
  })
}
