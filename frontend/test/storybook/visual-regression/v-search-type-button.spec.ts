import { expect, type Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { makeUrlWithArgs } from "~~/test/storybook/utils/args"
import { waitForResponse } from "~~/test/storybook/utils/response"

const urlWithArgs = makeUrlWithArgs(
  "components-vcontentswitcher-vsearchtypebutton--default-story"
)

const searchTypeButtonLocator = 'button[aria-haspopup="dialog"]'
const getIcon = (page: Page) =>
  page.locator(`${searchTypeButtonLocator} svg`).first()

test.describe.configure({ mode: "parallel" })

const goAndWaitForSvg = async (page: Page, url: string) => {
  await waitForResponse(page, url, /\.svg/)
  await expect(getIcon(page)).toBeVisible()
}

const buttonKinds = ["icon", "withTextLabel"] as const

test.describe("VSearchTypeButton", () => {
  for (const buttonKind of buttonKinds) {
    const showLabel = buttonKind === "withTextLabel"
    const buttonName = `button-${showLabel ? "with" : "without"}-text-label`

    for (const state of ["non-pressed", "pressed"] as const) {
      const snapshotName = `v-search-type-button-${buttonName}${state === "pressed" ? "-pressed" : ""}`
      breakpoints.describeMd(({ expectSnapshot }) => {
        test(`resting ${state} ${buttonName}`, async ({ page }) => {
          const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
          await goAndWaitForSvg(page, url)

          await expectSnapshot(
            `${snapshotName}-at-rest`,
            page.locator(searchTypeButtonLocator)
          )
        })

        test(`hovered ${state} ${buttonName}`, async ({ page }) => {
          const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
          await goAndWaitForSvg(page, url)
          await page.hover(searchTypeButtonLocator)

          await expectSnapshot(
            `${snapshotName}-hovered`,
            page.locator(searchTypeButtonLocator)
          )
        })
      })
    }
  }
})
