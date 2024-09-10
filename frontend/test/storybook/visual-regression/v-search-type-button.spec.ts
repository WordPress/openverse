import { expect, type Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { makeUrlWithArgs } from "~~/test/storybook/utils/args"
import { t } from "~~/test/playwright/utils/i18n"

const urlWithArgs = makeUrlWithArgs(
  "components-vcontentswitcher-vsearchtypebutton--default"
)

const searchTypeButtonName = t("searchType.selectLabel").replace(
  "{type}",
  "All"
)
const getSearchTypeButton = (page: Page) =>
  page.getByRole("button", { name: searchTypeButtonName })
test.describe.configure({ mode: "parallel" })

const goAndWaitForSvg = async (page: Page, url: string) => {
  await page.goto(url)
  await page.getByRole("button", { name: "Render Story" }).click()

  await expect(getSearchTypeButton(page)).toBeVisible()
  await expect(getSearchTypeButton(page).locator("svg").first()).toBeVisible()
}

const buttonKinds = ["icon", "withTextLabel"] as const

test.describe("VSearchTypeButton", () => {
  for (const buttonKind of buttonKinds) {
    const showLabel = buttonKind === "withTextLabel"
    const buttonName = `button-${showLabel ? "with" : "without"}-text-label`

    for (const state of ["non-pressed", "pressed"] as const) {
      const snapshotName = `v-search-type-button-${buttonName}${state === "pressed" ? "-pressed" : ""}`
      breakpoints.describeMd(({ breakpoint }) => {
        test(`resting ${state} ${buttonName}`, async ({ page }) => {
          const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
          await goAndWaitForSvg(page, url)

          await expect(getSearchTypeButton(page)).toHaveScreenshot(
            `${snapshotName}-at-rest-${breakpoint}.png`
          )
        })

        test(`hovered ${state} ${buttonName}`, async ({ page }) => {
          const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
          await goAndWaitForSvg(page, url)
          await getSearchTypeButton(page).hover()

          await expect(getSearchTypeButton(page)).toHaveScreenshot(
            `${snapshotName}-hovered-${breakpoint}.png`
          )
        })
      })
    }
  }
})
