import { test, expect } from "@playwright/test"

import { preparePageForTests, t } from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

test.describe("collections", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl", {
      features: {
        additional_search_views: "on",
      },
    })
    await page.goto("/image/f9384235-b72e-4f1e-9b05-e1b116262a29?q=cat")
  })

  test("can open tags collection page from image page", async ({ page }) => {
    // Using the href because there are multiple links with the same text.
    await page.click('[href*="/tag/cat"]')

    await expect(
      page.getByRole("button", { name: t("browsePage.load") })
    ).toBeEnabled()

    await expect(
      page.getByRole("heading", { level: 1, name: /cat/i })
    ).toBeVisible()
    expect(await page.locator("figure").count()).toEqual(20)
    expect(page.url()).toMatch(/image\/tag\/cat/)
  })
  test("can open source collection page from image page", async ({ page }) => {
    const sourcePattern = /flickr/i

    await page.getByRole("link", { name: sourcePattern }).first().click()

    await expect(
      page.getByRole("button", { name: t("browsePage.load") })
    ).toBeEnabled()

    await expect(
      page.getByRole("heading", { level: 1, name: sourcePattern })
    ).toBeVisible()

    expect(await page.locator("figure").count()).toEqual(20)

    expect(page.url()).toMatch(/image\/source\/flickr\/$/)
  })
  test("can open creator collection page from image page", async ({ page }) => {
    const creatorPattern = /strogoscope/i
    await page.getByRole("link", { name: creatorPattern }).first().click()

    await expect(
      page.getByRole("button", { name: t("browsePage.load") })
    ).toBeEnabled()

    await expect(
      page.getByRole("heading", { level: 1, name: creatorPattern })
    ).toBeVisible()

    expect(await page.locator("figure").count()).toEqual(20)

    expect(page.url()).toMatch(/image\/source\/flickr\/creator\/strogoscope\//)
  })
})
