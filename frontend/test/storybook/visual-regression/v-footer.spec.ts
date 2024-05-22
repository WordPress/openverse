import { expect, Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import {
  type LanguageDirection,
  languageDirections,
  t,
} from "~~/test/playwright/utils/i18n"

import { dirParam } from "~~/test/storybook/utils/args"

const footerKinds = ["internal", "content"] as const

const storyUrl = (
  footerKind: (typeof footerKinds)[number],
  dir: LanguageDirection
) => `/iframe.html?id=components-vfooter--${footerKind}${dirParam(dir)}`

/**
 * Changes the language using the language select, and checks for elements to
 * be visible to ensure that the page is fully-loaded.
 */
const setLanguageDirection = async (
  page: Page,
  dir: LanguageDirection,
  footerKind: (typeof footerKinds)[number]
) => {
  if (dir !== "rtl") {
    return
  }
  await page.locator("#language").selectOption({ value: "ar" })
  if (footerKind === "internal") {
    // The WP svg inside a link. The text with a placeholder is flaky in RTL.
    await expect(page.locator("a svg")).toBeVisible()
  } else {
    const aboutLink = page.getByText(t("navigation.about", "rtl"))
    await expect(aboutLink).toBeVisible()
  }
}

test.describe.configure({ mode: "parallel" })

test.describe("VFooter", () => {
  for (const dir of languageDirections) {
    for (const footerKind of footerKinds) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test(`footer-${footerKind}-${dir}`, async ({ page }) => {
          await page.goto(storyUrl(footerKind, dir))

          await setLanguageDirection(page, dir, footerKind)

          await expectSnapshot(
            `footer-${footerKind}-${dir}`,
            page.locator("footer")
          )
        })
      })
    }
  }
})
