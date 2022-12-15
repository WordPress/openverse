import { expect, test } from "@playwright/test"

test.describe.configure({ mode: "parallel" })
const wrapperLocator = ".wrapper"
test.describe("VSearchBarButton", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(
      "/iframe.html?id=components-vheader-vheadermobile-vsearchbarbutton--clear-and-back-buttons"
    )
  })
  test("Clear and back buttons resting", async ({ page }) => {
    expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
      name: `clear-back-buttons-resting.png`,
    })
  })

  test(`Back button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(1)")
    expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
      name: `back-button-hovered.png`,
    })
  })
  test(`Back button focused`, async ({ page }) => {
    await page.focus(".wrapper>button:nth-child(1)")
    expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
      name: `back-button-focused.png`,
    })
  })
  test(`Clear button hovered`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
      name: `clear-button-hovered.png`,
    })
  })
  test(`Clear button focused`, async ({ page }) => {
    await page.hover(".wrapper>button:nth-child(2)")
    expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
      name: `clear-button-focused.png`,
    })
  })
})
