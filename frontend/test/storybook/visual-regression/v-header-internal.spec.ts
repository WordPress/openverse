import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { languageDirections } from "~~/test/playwright/utils/i18n"
import { waitForResponse } from "~~/test/storybook/utils/response"
import { dirParam } from "~~/test/storybook/utils/args"

const headerSelector = ".main-header"
const defaultUrl =
  "/iframe.html?id=components-vheader-vheaderinternal--default-story"

const buttonSelector = "button[aria-haspopup='dialog']"

test.describe.configure({ mode: "parallel" })

test.describe("VHeaderInternal", () => {
  for (const dir of languageDirections) {
    const url = `${defaultUrl}${dirParam(dir)}`
    breakpoints.describeEachDesktop(({ expectSnapshot }) => {
      test(`desktop-header-internal-${dir}`, async ({ page }) => {
        await page.goto(url)
        await page.mouse.move(0, 150)

        await expectSnapshot(
          `desktop-header-internal-${dir}`,
          page.locator(headerSelector)
        )
      })
    })

    breakpoints.describeEachMobile(({ expectSnapshot }) => {
      test(`mobile-header-internal-${dir}`, async ({ page }) => {
        // Ensure svg is loaded before taking the snapshot
        await waitForResponse(page, url, /\.svg/)
        await expect(page.locator(`${buttonSelector} svg`)).toBeVisible()
        await page.mouse.move(0, 150)

        await expectSnapshot(
          `mobile-header-internal-closed-${dir}`,
          page.locator(headerSelector)
        )
      })

      test(`mobile-header-internal-modal-${dir}`, async ({ page }) => {
        await page.goto(url)

        // Ensure fonts are loaded before taking the snapshot.
        // The promise is awaited after the click to prevent race conditions.
        // https://playwright.dev/docs/api/class-page#page-wait-for-response
        const responsePromise = page.waitForResponse(/var\.woff2/)
        await page.locator(buttonSelector).click()
        await responsePromise
        // Mouse stays over the button, so the close button is hovered.
        // To prevent this, move the mouse away.
        await page.mouse.move(0, 0)

        await expectSnapshot(`mobile-header-internal-open-${dir}`, page)
      })
    })
  }
})
