import { test, expect } from '@playwright/test'

test.describe('v-checkbox', () => {
  test.describe('default', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/iframe.html?id=components-vcheckbox--default-story')
    })

    test('default', async ({ page }) => {
      expect(await page.screenshot()).toMatchSnapshot({ name: 'default.png' })
    })

    test('on', async ({ page }) => {
      await page.click('input[type="checkbox"]')
      expect(await page.screenshot()).toMatchSnapshot({ name: 'on.png' })
    })

    test('off', async ({ page }) => {
      // toggle on and off again
      await page.click('input[type="checkbox"]')
      // `force: true` is required because the `input`'s pointer events are actually intercepted by the visual SVG.
      // We still want to check that it works though as that does mimic the user behavior of checking directly on the checkbox.
      await page.click('input[type="checkbox"]', { force: true })
      expect(await page.screenshot()).toMatchSnapshot({ name: 'off.png' })
    })
  })
})
