import { test, expect, Page } from "@playwright/test"

import {
  enableNewHeader,
  isMobileMenuOpen,
  scrollToBottom,
  setCookies,
  t,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

const modalCloseButton = 'div[role="dialog"] >> [aria-label="Close"]'
const currentPageLink = 'div[role="dialog"] >> [aria-current="page"]'
const currentPageLinkInPopover = '.popover-content >> [aria-current="page"]'
const menuButton = `[aria-label="${t("header.aria.menu")}"]`

const clickMenuButton = async (page: Page) => await page.click(menuButton)
const closeMenu = async (page: Page) => await page.click(modalCloseButton)

const isPagesPopoverOpen = async (page: Page) =>
  page.locator(".popover-content").isVisible({ timeout: 100 })

test.describe("Header internal", () => {
  breakpoints.describeXs(() => {
    test.beforeEach(async ({ context, page }) => {
      await setCookies(context, { uiBreakpoint: "xs" })
      await enableNewHeader(page)
      await page.goto("/about")
    })

    test("can open and close the modal on xs breakpoint", async ({ page }) => {
      await clickMenuButton(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await expect(page.locator(currentPageLink)).toBeVisible()
      await expect(page.locator(currentPageLink)).toHaveText("About")

      await closeMenu(page)
      expect(await isMobileMenuOpen(page)).toBe(false)
      await expect(page.locator(menuButton)).toBeVisible()
    })

    test("the modal locks the scroll on xs breakpoint", async ({ page }) => {
      await scrollToBottom(page)

      await clickMenuButton(page)
      await closeMenu(page)

      const scrollPosition = await page.evaluate(() => window.scrollY)
      expect(scrollPosition).toBeGreaterThan(100)
    })

    test("the modal opens an external link in a new window and it closes the modal", async ({
      page,
    }) => {
      await scrollToBottom(page)
      await clickMenuButton(page)

      // Open the external link in a new tab, close the tab
      const [popup] = await Promise.all([
        page.waitForEvent("popup"),
        page.locator('div[role="dialog"] >> text=API').click(),
      ])
      await popup.close()
      // If we want the modal to stay open, we'll need to change this to `true`,
      // and implement the change
      expect(await isMobileMenuOpen(page)).toBe(false)
    })
  })

  breakpoints.describeMd(() => {
    test("can open and close the popover on sm breakpoint", async ({
      context,
      page,
    }) => {
      await setCookies(context, { breakpoint: "sm" })
      await enableNewHeader(page)
      await page.goto("/about")
      await clickMenuButton(page)
      expect(await isPagesPopoverOpen(page)).toBe(true)
      await expect(page.locator(currentPageLinkInPopover)).toBeVisible()
      await expect(page.locator(currentPageLinkInPopover)).toHaveText("About")

      await clickMenuButton(page)
      expect(await isPagesPopoverOpen(page)).toBe(false)
      await expect(page.locator(menuButton)).toBeVisible()
    })
  })
})
