import { expect, test } from '@playwright/test'

const apiBase = process.env.SCENEMIND_E2E_API_URL ?? 'http://127.0.0.1:18000/api/v1'
const imagePath = process.env.SCENEMIND_E2E_IMAGE

test.describe.configure({ mode: 'serial' })

test('analysis saves evidence and opens memory detail', async ({ page }) => {
  if (!imagePath) throw new Error('SCENEMIND_E2E_IMAGE is required')
  await page.goto('/analyze')
  await expect(page.locator('.page-heading .eyebrow')).toHaveText('SCENE ANALYSIS')
  await page.locator('input[type=file]').setInputFiles(imagePath)
  await page.locator('.analysis-actions .primary-button').click()
  await expect(page.locator('.success-message')).toBeVisible()
  await expect(page.locator('.object-grid')).toBeVisible()
  await page.locator('.success-message a').click()
  await expect(page).toHaveURL(/\/memory\/[0-9a-f-]+$/)
})

test('memory search returns last-seen and history evidence', async ({ page }) => {
  await page.goto('/memory')
  await page.locator('.memory-search input').fill('cup')
  await page.locator('.memory-search button').click()
  await expect(page.locator('.last-seen-section')).toBeVisible()
  await expect(page.locator('.history-timeline')).toBeVisible()
  await expect(page.locator('.history-timeline a').first()).toBeVisible()
})

test('Agent shows grounded answer, trace, and evidence detail', async ({ page }) => {
  await page.goto('/agent')
  await page.locator('#agent-question').fill('Where was my cup last seen?')
  await page.locator('.agent-query button').click()
  await expect(page.locator('.agent-answer-card')).toBeVisible()
  await expect(page.locator('.agent-evidence-grid')).toBeVisible()
  await page.locator('.tool-trace summary').click()
  await expect(page.locator('.tool-trace article').first()).toBeVisible()
  await expect(page.locator('.agent-evidence-grid a').first()).toBeVisible()
})

test('seeded session opens a persisted timeline', async ({ page }) => {
  await page.goto('/sessions')
  await expect(page.locator('.session-card').first()).toBeVisible()
  await page.locator('.session-card').first().click()
  await expect(page).toHaveURL(/\/sessions\/[0-9a-f-]+$/)
  await expect(page.locator('.observation-timeline, .session-counters').first()).toBeVisible()
})

test('devices, insights, glasses disclaimer, and system are observable', async ({ page }) => {
  await page.goto('/devices')
  await expect(page.getByText('AI Glasses Simulator', { exact: true })).toBeVisible()
  await page.goto('/glasses')
  await expect(page.locator('.simulator-disclaimer')).toBeVisible()
  await expect(page.locator('.page-heading span')).toHaveText('Simulator')
  await page.goto('/insights')
  await expect(page.locator('.insights-layout')).toBeVisible()
  await page.goto('/system')
  await expect(page.locator('.page-heading .eyebrow')).toHaveText('COMPETITION READINESS')
  await expect(page.locator('.page-heading > span')).toHaveText('ready')
  await expect(page.locator('.system-details')).toContainText('C')
})

test('empty database states remain truthful', async ({ page, request }) => {
  const sessions = await (await request.get(`${apiBase}/capture-sessions`)).json()
  for (const item of sessions.items) {
    if (item.status === 'active') await request.post(`${apiBase}/capture-sessions/${item.id}/stop`)
    await request.delete(`${apiBase}/capture-sessions/${item.id}`)
  }
  const observations = await (await request.get(`${apiBase}/observations?limit=100`)).json()
  for (const item of observations.items) await request.delete(`${apiBase}/observations/${item.id}`)

  await page.goto('/memory')
  await expect(page.locator('.memory-empty')).toBeVisible()
  await page.goto('/agent')
  await page.locator('#agent-question').fill('Where was the missing umbrella last seen?')
  await page.locator('.agent-query button').click()
  await expect(page.locator('.agent-empty')).toBeVisible()
  await page.goto('/insights')
  await expect(page.locator('.memory-empty')).toBeVisible()
  await page.goto('/sessions')
  await expect(page.locator('.memory-empty')).toBeVisible()
})
