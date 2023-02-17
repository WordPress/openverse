import { expect, Page, test } from "@playwright/test"

import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  goToSearchTerm,
  searchTypePath,
  t,
} from "~~/test/playwright/utils/navigation"

import { supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

for (const searchType of supportedSearchTypes) {
  test(`can change type and search for ${searchType} from homepage`, async ({
    page,
  }) => {
    await goToSearchTerm(page, "cat", {
      searchType,
      mode: "CSR",
    })

    const expectedUrl = `/search/${searchTypePath(searchType)}?q=cat`
    await expect(page).toHaveURL(expectedUrl)
  })
}

const searchTypePopover = "[aria-labelledby='search-type-button'] > div"

const popoverIsVisible = async (page: Page) =>
  await expect(page.locator(searchTypePopover)).toBeVisible()
const popoverIsNotVisible = async (page: Page) =>
  await expect(page.locator(searchTypePopover)).not.toBeVisible()
const clickPopoverButton = async (page: Page) =>
  await page.getByRole("button", { name: t("search-type.all") }).click()

test("can close the search type popover by clicking outside", async ({
  page,
}) => {
  await page.goto("/")
  await clickPopoverButton(page)
  await popoverIsVisible(page)

  await page.mouse.click(1, 1)
  await popoverIsNotVisible(page)
})

test("can close the search type popover by pressing Escape", async ({
  page,
}) => {
  await page.goto("/")
  await clickPopoverButton(page)
  await popoverIsVisible(page)

  await page.keyboard.press("Escape")

  await popoverIsNotVisible(page)
})
