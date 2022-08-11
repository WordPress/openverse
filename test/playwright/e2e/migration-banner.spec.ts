import { test, expect } from '@playwright/test'

test.describe.configure({ mode: 'parallel' })

test.describe('migration banner', () => {
  test('shows migration banner on homepage', async ({ page }) => {
    await page.goto('/?referrer=creativecommons.org')

    const migrationNotice = page.locator('[data-testid="banner-cc-referral"]')
    const message = 'CC Search is now called Openverse'

    await expect(migrationNotice).toContainText(message)
    await expect(migrationNotice).toBeVisible()
  })

  test('migration banner goes away on navigation', async ({ page }) => {
    await page.goto('/?referrer=creativecommons.org')

    const migrationNotice = page.locator('[data-testid="banner-cc-referral"]')
    await expect(migrationNotice).toBeVisible()

    // Navigate away from the page
    await Promise.all([
      page.locator('a.homepage-image').first().click(),
      page.waitForLoadState('domcontentloaded'),
    ])
    await expect(migrationNotice).toBeHidden()
  })

  test('migration banner is dismissable and stays dismissed', async ({
    page,
  }) => {
    await page.goto('/?referrer=creativecommons.org')

    const migrationNotice = page.locator('[data-testid="banner-cc-referral"]')
    await expect(migrationNotice).toBeVisible({ timeout: 500 })

    await migrationNotice
      .locator('[aria-label="Close"]:visible')
      .click({ timeout: 500 })
    await expect(migrationNotice).not.toBeVisible({ timeout: 500 })

    await page.reload()
    await expect(migrationNotice).not.toBeVisible({ timeout: 500 })
  })
})
