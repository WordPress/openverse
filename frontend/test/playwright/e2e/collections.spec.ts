/**
 * The commented-out assertions will be re-enabled after the fetching
 * of collections is fixed using `VMediaCollection` component
 * introduced in https://github.com/WordPress/openverse/pull/3831
 */

import { test, expect } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"
import {
  getCopyButton,
  getH1,
  // getLoadMoreButton,
} from "~~/test/playwright/utils/components"

test.describe.configure({ mode: "parallel" })

test.describe("collections", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl", {
      features: {
        additional_search_views: "on",
      },
    })
    await page.goto("/image/f9384235-b72e-4f1e-9b05-e1b116262a29")
    // Wait for the page to hydrate
    await expect(getCopyButton(page)).toBeEnabled()
  })

  test("can open tags collection page from image page", async ({ page }) => {
    // Using the href because there are multiple links with the same text.
    await page.click('[href*="image/collection?tag="]')

    await page.waitForURL(/image\/collection/)

    await expect(getH1(page, /cat/i)).toBeVisible()
    // await expect(getLoadMoreButton(page)).toBeEnabled()
    // expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open source collection page from image page", async ({ page }) => {
    const sourcePattern = /flickr/i

    await page.getByRole("link", { name: sourcePattern }).first().click()

    await page.waitForURL(/image\/collection/)

    await expect(getH1(page, sourcePattern)).toBeVisible()
    // await expect(getLoadMoreButton(page)).toBeEnabled()
    // expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open creator collection page from image page", async ({ page }) => {
    const creatorPattern = /strogoscope/i
    await page.getByRole("link", { name: creatorPattern }).first().click()

    await page.waitForURL(/image\/collection/)

    await expect(getH1(page, creatorPattern)).toBeVisible()
    // await expect(getLoadMoreButton(page)).toBeEnabled()
    // expect(await page.locator("figure").count()).toEqual(20)
  })
})
