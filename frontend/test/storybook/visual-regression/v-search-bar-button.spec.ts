import { test } from "~~/test/playwright/utils/test"
import { expectSnapshot } from "~~/test/playwright/utils/expect-snapshot"

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
      page,
      "clear-and-back-buttons-resting",
      page.locator(wrapperLocator)
    )
  })

  test(`Back button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(1)")
    await expectSnapshot(
      page,
      "back-button-hovered",
      page.locator(wrapperLocator)
    )
  })
  test(`Back button focused`, async ({ page }) => {
    await page.focus(".wrapper>button:nth-child(1)")
    await expectSnapshot(
      page,
      "back-button-focused",
      page.locator(wrapperLocator)
    )
  })
  test(`Clear button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    await expectSnapshot(
      page,
      "clear-button-hovered",
      page.locator(wrapperLocator)
    )
  })
  test(`Clear button focused`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    await expectSnapshot(
      page,
      "clear-button-focused",
      page.locator(wrapperLocator)
    )
  })
})
