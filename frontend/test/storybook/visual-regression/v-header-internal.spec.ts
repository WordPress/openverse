import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  type LanguageDirection,
  languageDirections,
} from "~~/test/playwright/utils/i18n"
import { dirParam } from "~~/test/storybook/utils/args"

const headerSelector = ".main-header"
const defaultUrl =
  "/iframe.html?id=components-vheader-vheaderinternal--default-story"
const pageUrl = (dir: LanguageDirection) => `${defaultUrl}${dirParam(dir)}`

test.describe.configure({ mode: "parallel" })

test.describe("VHeaderInternal", () => {
  for (const dir of languageDirections) {
    test.describe(`${dir}`, () => {
      breakpoints.describeEachDesktop(({ expectSnapshot }) => {
        test(`desktop header`, async ({ page }) => {
          await page.goto(pageUrl(dir))
          await page.mouse.move(0, 150)
          await expectSnapshot(
            `desktop-header-internal-${dir}`,
            page.locator(headerSelector)
          )
        })
      })
      breakpoints.describeEachMobile(({ breakpoint, expectSnapshot }) => {
        test(`mobile header closed`, async ({ page }) => {
          await page.goto(pageUrl(dir))
          await page.mouse.move(0, 150)

          await expect(page.locator(headerSelector)).toHaveScreenshot(
            `mobile-header-internal-closed-${dir}-${breakpoint}.png`
          )
        })

        test(`mobil header with open modal`, async ({ page }) => {
          await page.goto(pageUrl(dir))

          // Ensure fonts are loaded before taking the snapshot
          const responsePromise = page.waitForResponse(/var\.woff2/)
          await page.locator('button[aria-haspopup="dialog"]').click()
          await responsePromise
          // Mouse stays over the button, so the close button is hovered.
          // To prevent this, move the mouse away.
          await page.mouse.move(0, 0)

          await expectSnapshot(`mobile-header-internal-open-${dir}`, page)
        })
      })
    })
  }
})
