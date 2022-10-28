import { test, expect, Page } from '@playwright/test'

import {
  enableNewHeader,
  isMobileMenuOpen,
  scrollToBottom,
  t,
} from '~~/test/playwright/utils/navigation'
import breakpoints from '~~/test/playwright/utils/breakpoints'

const modalCloseButton = 'div[role="dialog"] >> [aria-label="Close"]'
const currentPageLink = 'div[role="dialog"] >> [aria-current="page"]'
const menuButton = `[aria-label="${t('header.aria.menu')}"]`

const openMenu = async (page: Page) => await page.click(menuButton)
const closeMenu = async (page: Page) => await page.click(modalCloseButton)

test.describe('Header internal', () => {
  breakpoints.describeSm(() => {
    test.beforeEach(async ({ page }) => {
      await enableNewHeader(page)
      await page.goto('/about')
    })
    test('can open and close the modal on md breakpoint', async ({ page }) => {
      await openMenu(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await expect(page.locator(currentPageLink)).toBeVisible()
      await expect(page.locator(currentPageLink)).toHaveText('About')

      await closeMenu(page)
      expect(await isMobileMenuOpen(page)).toBe(false)
      await expect(page.locator(menuButton)).toBeVisible()
    })

    test('the modal locks the scroll on md breakpoint', async ({ page }) => {
      await scrollToBottom(page)

      await openMenu(page)
      await closeMenu(page)

      const scrollPosition = await page.evaluate(() => window.scrollY)
      expect(scrollPosition).toBeGreaterThan(100)
    })

    test("the modal opens an external link in a new window and it doesn't close the modal", async ({
      page,
    }) => {
      await scrollToBottom(page)
      await openMenu(page)

      // Open the external link in a new tab, close the tab
      const [popup] = await Promise.all([
        page.waitForEvent('popup'),
        page.locator('div[role="dialog"] >> text=API').click(),
      ])
      await popup.close()

      expect(await isMobileMenuOpen(page)).toBe(true)
    })
  })
})
