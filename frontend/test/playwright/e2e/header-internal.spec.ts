import { expect, Page, test } from "@playwright/test"

import {
  isDialogOpen,
  openAndCloseExternalLink,
  preparePageForTests,
  scrollToBottom,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import { LanguageDirection, t } from "~~/test/playwright/utils/i18n"
import { getHomeLink, getMenuButton } from "~~/test/playwright/utils/components"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

const currentPageLink = 'div[role="dialog"] >> [aria-current="page"]'
const currentPageLinkInPopover = '.popover-content >> [aria-current="page"]'

const clickMenuButton = async (page: Page) => {
  await getMenuButton(page).click()
}

const closeMenu = async (page: Page, dir: LanguageDirection = "ltr") => {
  await page
    .getByRole("button", { name: t("modal.closePagesMenu", dir) })
    .click()
}

const isPagesPopoverOpen = async (page: Page) =>
  page.locator(".popover-content").isVisible({ timeout: 100 })

const aboutPageTitle = t("about.title")

test.describe.configure({ mode: "parallel" })

test.describe("Header internal", () => {
  breakpoints.describeXs(() => {
    test.beforeEach(async ({ page }) => {
      await preparePageForTests(page, "xs")
    })

    test("can open and close the modal on xs breakpoint", async ({ page }) => {
      await page.goto("/about")
      await clickMenuButton(page)
      expect(await isDialogOpen(page)).toBe(true)
      await expect(page.locator(currentPageLink)).toBeVisible()
      await expect(page.locator(currentPageLink)).toHaveText(
        t("navigation.about")
      )

      await closeMenu(page)
      expect(await isDialogOpen(page)).toBe(false)
      await expect(getMenuButton(page)).toBeVisible()
    })

    test("the modal locks the scroll on xs breakpoint", async ({ page }) => {
      await page.goto("/about")

      // Wait for hydration
      await expect(getMenuButton(page)).toBeEnabled()
      await scrollToBottom(page)

      await clickMenuButton(page)
      await closeMenu(page)

      const scrollPosition = await page.evaluate(() => window.scrollY)
      expect(scrollPosition).toBeGreaterThan(100)
    })

    test("the modal opens an external link in the same window and the modal is closed on back click", async ({
      page,
    }) => {
      await page.goto("/about")
      await scrollToBottom(page)
      await clickMenuButton(page)

      await openAndCloseExternalLink(page, {
        locator: page.locator('div[role="dialog"] >> text=API'),
      })

      expect(await isDialogOpen(page)).toBe(false)
    })

    test("content page opened from home should be scrollable", async ({
      page,
    }) => {
      await page.goto("/")
      await clickMenuButton(page)
      await page.getByRole("link", { name: t("navigation.about") }).click()
      await page.waitForURL("/about")

      const pageTitleRegex = new RegExp(aboutPageTitle, "i")
      // For some reason during this test the navigation overlay sometimes takes ~5-9 ms
      // During that time, the page cannot scroll. We just need to wait for the
      // page's title to be visible before going on.
      await page
        .getByRole("heading", { level: 1, name: pageTitleRegex })
        .waitFor({ state: "visible" })
      await scrollToBottom(page)
      const scrollPosition = await page.evaluate(() => window.scrollY)
      expect(scrollPosition).toBeGreaterThan(100)
    })

    test("can open a content page from home and go back", async ({ page }) => {
      await page.goto("/")
      const homeUrl = page.url()
      await clickMenuButton(page)
      await page.getByRole("link", { name: t("navigation.about") }).click()

      await getHomeLink(page).click()
      await page.waitForURL(homeUrl)
      expect(page.url()).toBe(homeUrl)
    })

    test("sends OPEN_PAGES_MENU event", async ({ context, page }) => {
      const events = collectAnalyticsEvents(context)
      await page.goto("/")
      await clickMenuButton(page)
      const openPagesMenuEvent = events.find((e) => e.n === "OPEN_PAGES_MENU")
      expectEventPayloadToMatch(openPagesMenuEvent, {})
    })
  })

  breakpoints.describeMd(() => {
    test("can open and close the popover on sm breakpoint", async ({
      page,
    }) => {
      await preparePageForTests(page, "sm")
      await page.goto("/about")
      await clickMenuButton(page)
      expect(await isPagesPopoverOpen(page)).toBe(true)
      await expect(page.locator(currentPageLinkInPopover)).toBeVisible()
      await expect(page.locator(currentPageLinkInPopover)).toHaveText(
        t("navigation.about")
      )

      await clickMenuButton(page)
      expect(await isPagesPopoverOpen(page)).toBe(false)
      await expect(getMenuButton(page)).toBeVisible()
    })
  })
})
