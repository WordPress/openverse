import { test } from "@playwright/test"

import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

test.describe.configure({ mode: "parallel" })
const wrapperLocator = ".wrapper"
test.describe("VSearchBarButton", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(
      "/iframe.html?id=components-vheader-vheadermobile-vsearchbarbutton--clear-and-back-buttons"
    )
  })
  test("Clear and back buttons resting", async ({ page }) => {
    await expectSnapshot(
      "clear-and-back-buttons-resting",
      page.locator(wrapperLocator)
    )
  })

  test(`Back button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(1)")
    await expectSnapshot("back-button-hovered", page.locator(wrapperLocator))
  })
  test(`Back button focused`, async ({ page }) => {
    await page.focus(".wrapper>button:nth-child(1)")
    await expectSnapshot("back-button-focused", page.locator(wrapperLocator))
  })
  test(`Clear button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    await expectSnapshot("clear-button-hovered", page.locator(wrapperLocator))
  })
  test(`Clear button focused`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    await expectSnapshot("clear-button-focused", page.locator(wrapperLocator))
  })
})
