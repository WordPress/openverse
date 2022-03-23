import { test, expect } from '@playwright/test'

test('shows migration banner on homepage', async ({ page }) => {
  await page.goto('/?referrer=creativecommons.org')

  const migrationNotice = page.locator('.cc-ov-migration')
  const message = 'CC Search is now called Openverse'

  await expect(migrationNotice).toContainText(message)
  await expect(migrationNotice).toBeVisible()
})

test('migration banner goes away on navigation', async ({ page }) => {
  await page.goto('/?referrer=creativecommons.org')

  const migrationNotice = page.locator('.cc-ov-migration')
  await expect(migrationNotice).toBeVisible()

  // Navigate away from the page
  await Promise.all([
    page.locator('a.homepage-image').first().click(),
    page.waitForLoadState('domcontentloaded'),
  ])
  await expect(migrationNotice).toBeHidden()
})
