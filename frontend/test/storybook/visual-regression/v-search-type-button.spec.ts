import { expect, type Page, test } from "@playwright/test"

import { makeUrlWithArgs } from "~~/test/storybook/utils/args"
import { t } from "~~/test/playwright/utils/i18n"
import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

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
      test(`resting ${state} ${buttonName}`, async ({ page }) => {
        const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
        await goAndWaitForSvg(page, url)

        await expectSnapshot(
          `${snapshotName}-at-rest`,
          getSearchTypeButton(page)
        )
      })

      test(`hovered ${state} ${buttonName}`, async ({ page }) => {
        const url = urlWithArgs({ showLabel, pressed: state === "pressed" })
        await goAndWaitForSvg(page, url)
        await getSearchTypeButton(page).hover()

        await expectSnapshot(
          `${snapshotName}-hovered`,
          getSearchTypeButton(page)
        )
      })
    }
  }
})
