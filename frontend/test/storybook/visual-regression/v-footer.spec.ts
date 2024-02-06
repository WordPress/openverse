import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { languageDirections } from "~~/test/playwright/utils/i18n"

const footerKinds = ["internal", "content"] as const

const defaultUrl = "/iframe.html?id=components-vfooter--"

const pageUrl = (
  dir: (typeof languageDirections)[number],
  footerKind: (typeof footerKinds)[number]
) => {
  const url = `${defaultUrl}${footerKind}`
  return dir === "ltr" ? url : `${url}&globals=languageDirection:rtl`
}

test.describe.configure({ mode: "parallel" })

test.describe("VFooter", () => {
  for (const dir of languageDirections) {
    for (const footerKind of footerKinds) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test.beforeEach(async ({ page }) => {
          await page.goto(pageUrl(dir, footerKind))
          if (dir === "rtl") {
            await page.locator("#language").selectOption({ value: "ar" })
          }
        })

        test(`footer-${footerKind}-${dir}`, async ({ page }) => {
          await expectSnapshot(
            `footer-${footerKind}-${dir}`,
            page.locator("footer")
          )
        })
      })
    }
  }
})
