import { expect, test } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'

const imagePath = process.env.SCENEMIND_E2E_IMAGE
const apiBase = process.env.SCENEMIND_E2E_API_URL ?? 'http://127.0.0.1:18000/api/v1'
const reviewRoot = process.env.SCENEMIND_UI_REVIEW_DIR ?? '../artifacts/ui-review'
const viewports = [
  { name: 'desktop', width: 1440, height: 1000, screenshots: true },
  { name: 'desktop-1280', width: 1280, height: 800, screenshots: true },
  { name: 'tablet', width: 1024, height: 768, screenshots: true },
  { name: 'mobile', width: 390, height: 844, screenshots: true },
  { name: 'mobile-375', width: 375, height: 812, screenshots: true, reducedMotion: true },
]

test.describe.configure({ mode: 'serial' })

for (const viewport of viewports) {
  test(`UI review ${viewport.name} has no horizontal overflow`, async ({ page, request }) => {
    test.setTimeout(90_000)
    if (!imagePath) throw new Error('SCENEMIND_E2E_IMAGE is required')
    const consoleErrors: string[] = []
    page.on('console', (message) => {
      if (message.type() === 'error') consoleErrors.push(message.text())
    })
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    if ('reducedMotion' in viewport && viewport.reducedMotion) await page.emulateMedia({ reducedMotion: 'reduce' })

    await page.goto('/analyze')
    await page.locator('input[type=file]').setInputFiles(imagePath)
    await page.locator('.analysis-actions .primary-button').click()
    await expect(page.locator('.success-message')).toBeVisible()
    const observationsResponse = await request.get(`${apiBase}/observations?limit=1`)
    expect(observationsResponse.ok()).toBeTruthy()
    const observations = await observationsResponse.json() as { items: Array<{ id: string }> }
    expect(observations.items.length).toBeGreaterThan(0)

    const sessionResponse = await request.post(`${apiBase}/capture-sessions`, { data: {
      title: `UI review ${viewport.name}`, source_type: 'evaluation', sample_interval_seconds: 5,
      auto_save_mode: 'manual',
    } })
    expect(sessionResponse.ok()).toBeTruthy()
    const session = await sessionResponse.json() as { id: string }
    const routes = [
      ['01-home', '/'], ['02-live-lens', '/live'], ['03-analysis', '/analyze'], ['04-memory', '/memory'],
      ['05-observation-evidence', `/memory/${observations.items[0].id}`], ['06-agent-evidence', '/agent'],
      ['07-session-timeline', `/sessions/${session.id}`], ['08-devices', '/devices'],
      ['09-glasses-simulator', '/glasses'], ['10-insights', '/insights'], ['11-privacy', '/privacy'], ['12-system', '/system'],
    ]

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
      if (route === '/' && 'reducedMotion' in viewport && viewport.reducedMotion) {
        await expect(page.locator('.memory-core.quality-reduced')).toBeVisible()
      }
      if (viewport.screenshots) {
        // Keep keyboard-only affordances out of the review capture while preserving
        // the skip link for real keyboard users.
        await page.evaluate(() => window.scrollTo({ top: 0, left: 0, behavior: 'instant' }))
        await page.locator('#main-content').focus()
        await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
        const directory = path.resolve(reviewRoot, viewport.name)
        await mkdir(directory, { recursive: true })
        // Viewport captures avoid repeating fixed and sticky navigation while
        // Playwright stitches unusually tall pages.
        await page.screenshot({ path: path.join(directory, `${name}.png`), fullPage: false })
      }
    }
    expect(consoleErrors, `${viewport.name} console errors`).toEqual([])
  })
}
