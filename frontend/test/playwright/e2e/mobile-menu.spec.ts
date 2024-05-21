import { test, expect, type Page } from "@playwright/test"

import {
  goToSearchTerm,
  isDialogOpen,
  searchTypes,
  filters,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import { t } from "~~/test/playwright/utils/i18n"

const contentSettingsModal = async (page: Page) =>
  page.getByRole("dialog", { name: t("header.aria.menu") })

test.describe.configure({ mode: "parallel" })

breakpoints.describeXs(() => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xs")
  })
  test("Can open filters menu on mobile at least twice", async ({ page }) => {
    await goToSearchTerm(page, "cat", { searchType: "all", mode: "SSR" })

    await filters.open(page)
    expect(await isDialogOpen(page)).toBe(true)
    await filters.close(page)

    await filters.open(page)
    expect(await isDialogOpen(page)).toBe(true)
    await filters.close(page)
    expect(await isDialogOpen(page)).toBe(false)
  })

  test("Can open mobile menu at least twice", async ({ page }) => {
    await goToSearchTerm(page, "cat")
    await searchTypes.open(page)
    expect(await isDialogOpen(page)).toBe(true)
    await searchTypes.close(page)

    await searchTypes.open(page)
    expect(await isDialogOpen(page)).toBe(true)
    await searchTypes.close(page)
    expect(await isDialogOpen(page)).toBe(false)
  })

  test("Can open content settings with keyboard", async ({ page }) => {
    await goToSearchTerm(page, "galah")
    for (let i = 0; i < 4; i++) {
      await page.keyboard.press("Tab")
    }
    await page.keyboard.press("Enter")
    await expect(await contentSettingsModal(page)).toBeVisible()

    await page.keyboard.press("Escape")
    await expect(await contentSettingsModal(page)).toBeHidden()
  })
})
