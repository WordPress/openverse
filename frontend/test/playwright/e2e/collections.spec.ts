import { test, expect } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"
import {
  getCopyButton,
  getH1,
  getLoadMoreButton,
} from "~~/test/playwright/utils/components"

test.describe.configure({ mode: "parallel" })

test.describe("collections CSR", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl", {
      features: {
        additional_search_views: "on",
      },
    })
    await page.goto("/image/f9384235-b72e-4f1e-9b05-e1b116262a29?q=cat")
    // Wait for the page to hydrate
    await expect(getCopyButton(page)).toBeEnabled()
  })

  test("can open tags collection page from image page", async ({ page }) => {
    // Using the href because there are multiple links with the same text.
    const tag = "animals/cats&dogs"
    await page.getByRole("link", { name: tag }).click()

    await page.waitForURL(/image\/tag\//)

    await expect(getH1(page, tag)).toBeVisible()
    await expect(getLoadMoreButton(page)).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open source collection page from image page", async ({ page }) => {
    const sourcePattern = /flickr/i

    await page.getByRole("link", { name: sourcePattern }).first().click()

    await page.waitForURL(/image\/source\/flickr\//)

    await expect(getLoadMoreButton(page)).toBeEnabled()
    await expect(getH1(page, sourcePattern)).toBeVisible()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open creator collection page from image page", async ({ page }) => {
    const creator = "/strogoscope&ref=profile"
    await page.getByRole("link", { name: creator }).first().click()

    await page.waitForURL(/image\/source\/flickr\/creator\//)

    await expect(getH1(page, creator)).toBeVisible()
    await expect(getLoadMoreButton(page)).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })
})

test.describe("collections", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl", {
      features: {
        additional_search_views: "on",
      },
    })
  })

  test("can open localized creator collection page from image page", async ({
    page,
  }) => {
    await page.goto("/ar/image/f9384235-b72e-4f1e-9b05-e1b116262a29?q=cat")

    const creator = "/strogoscope&ref=profile"
    await page.getByRole("link", { name: creator }).first().click()

    await page.waitForURL(/image\/source\/flickr\/creator\//)

    await expect(getH1(page, creator)).toBeVisible()
    await expect(getLoadMoreButton(page, "rtl")).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open tags collection on SSR", async ({ page }) => {
    const tag = "animals/cats&dogs"
    await page.goto(`/image/tag/${encodeURIComponent(tag)}`)

    await expect(getH1(page, tag)).toBeVisible()
    await expect(getLoadMoreButton(page)).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open source collection on SSR", async ({ page }) => {
    await page.goto(`/image/source/flickr/`)

    await expect(getH1(page, "Flickr")).toBeVisible()
    await expect(getLoadMoreButton(page)).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open creator collection on SSR", async ({ page }) => {
    const creator = "/strogoscope&ref=profile"
    await page.goto(
      `/image/source/flickr/creator/${encodeURIComponent(creator)}`
    )

    await expect(getH1(page, creator)).toBeVisible()
    await expect(getLoadMoreButton(page)).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })

  test("can open localized creator collection on SSR", async ({ page }) => {
    const creator = "/strogoscope&ref=profile"
    await page.goto(
      `/ar/image/source/flickr/creator/${encodeURIComponent(creator)}`
    )

    await expect(getH1(page, creator)).toBeVisible()
    await expect(getLoadMoreButton(page, "rtl")).toBeEnabled()
    expect(await page.locator("figure").count()).toEqual(20)
  })
})
