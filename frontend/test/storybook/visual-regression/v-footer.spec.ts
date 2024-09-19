import { expect, Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import {
  type LanguageDirection,
  languageDirections,
} from "~~/test/playwright/utils/i18n"

import { dirParam } from "~~/test/storybook/utils/args"

const footerKinds = ["internal", "content"] as const

const storyUrl = (
  footerKind: (typeof footerKinds)[number],
  dir: LanguageDirection
) => `/iframe.html?id=components-vfooter--${footerKind}${dirParam(dir)}`

/**
 * TODO: Remove this when the theme selector is no longer highlighted.
 */
const disableNewHighlights = async (page: Page) => {
  const themeSwitcher = page.locator("#theme").nth(0)
  await themeSwitcher.click()
  await themeSwitcher.blur()
  await page.mouse.move(0, 0)
}

test.describe.configure({ mode: "parallel" })

test.describe("VFooter", () => {
  for (const dir of languageDirections) {
    for (const footerKind of footerKinds) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test(`footer-${footerKind}-${dir}`, async ({ page }) => {
          await page.goto(storyUrl(footerKind, dir))

          // Ensure the component is hydrated by checking that language or theme select is enabled
          await expect(page.getByRole("combobox").nth(0)).toBeEnabled()
          await disableNewHighlights(page)

          await expectSnapshot(
            page,
            `footer-${footerKind}`,
            page.locator("footer"),
            { dir }
          )
        })
      })
    }
  }
})
