import { expect, type Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

const defaultUrl = (showLabel: boolean) =>
  `/iframe.html?id=components-vcontentswitcher-vsearchtypebutton--default-story&args=showLabel:${showLabel}`
const pressedUrl = (showLabel: boolean) =>
  `${defaultUrl(showLabel)};pressed:true`

const searchTypeButtonLocator = 'button[aria-haspopup="dialog"]'
const getIcon = (page: Page) =>
  page.locator('button[aria-haspopup="dialog"] svg').first()

test.describe.configure({ mode: "parallel" })

const goAndWaitForSvg = async (page: Page, url: string) => {
  const response = page.waitForResponse(/\.svg/)
  await page.goto(url)
  await response
  await expect(getIcon(page)).toBeVisible()
}

const buttonKinds = ["icon", "withTextLabel"] as const
test.describe("VSearchTypeButton", () => {
  for (const buttonKind of buttonKinds) {
    const showLabel = buttonKind === "withTextLabel"
    const buttonName = `button-${showLabel ? "with" : "without"}-text-label`
    breakpoints.describeMd(({ expectSnapshot }) => {
      test(`resting ${buttonName}`, async ({ page }) => {
        await goAndWaitForSvg(page, defaultUrl(showLabel))

        await expectSnapshot(
          `v-search-type-button-${buttonName}-at-rest`,
          page.locator(searchTypeButtonLocator)
        )
      })

      test(`hovered ${buttonName}`, async ({ page }) => {
        await goAndWaitForSvg(page, defaultUrl(showLabel))
        await page.hover(searchTypeButtonLocator)

        await expectSnapshot(
          `v-search-type-button-${buttonName}-hovered`,
          page.locator(searchTypeButtonLocator)
        )
      })

      test(`pressed ${buttonName}`, async ({ page }) => {
        await goAndWaitForSvg(page, pressedUrl(showLabel))

        await expectSnapshot(
          `v-search-type-button-${buttonName}-pressed`,
          page.locator(searchTypeButtonLocator)
        )
      })

      test(`pressed hovered ${buttonName}`, async ({ page }) => {
        await goAndWaitForSvg(page, pressedUrl(showLabel))

        await page.hover(searchTypeButtonLocator)

        await expectSnapshot(
          `v-search-type-button-${buttonName}-pressed-hovered`,
          page.locator(searchTypeButtonLocator)
        )
      })
    })
  }
})
