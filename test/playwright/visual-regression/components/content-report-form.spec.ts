import { test, expect } from '@playwright/test'

test.describe('content report form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/image/feb91b13-422d-46fa-8ef4-cbf1e6ddee9b')
  })

  test('unfocused close button', async ({ page }) => {
    await page.click('button:has-text("report")', { timeout: 500 })
    const form = page.locator('[data-testid="content-report-popover"]')

    expect(await form.screenshot({ timeout: 500 })).toMatchSnapshot({
      name: 'content-report-unfocused.png',
    })
  })

  test('focused close button', async ({ page }) => {
    await page.click('button:has-text("report")', { timeout: 500 })
    const form = page.locator('[data-testid="content-report-popover"]')

    await form.locator('[aria-label="Close"]').focus({ timeout: 500 })
    expect(await form.screenshot()).toMatchSnapshot({
      name: 'content-report-focused.png',
    })
  })
})
