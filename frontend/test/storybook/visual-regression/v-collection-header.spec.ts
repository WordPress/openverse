import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe("VCollectionHeader", () => {
  breakpoints.describeMobileAndDesktop(({ expectSnapshot }) => {
    for (const languageDirection of ["ltr", "rtl"]) {
      for (const collection of [
        "tag",
        "creator",
        "source",
        "source-with-long-name",
      ]) {
        test(`${collection}-${languageDirection}`, async ({ page }) => {
          await page.goto(
            `/iframe.html?id=components-vcollectionheader--default-story&args=id:${collection}`
          )
          await expectSnapshot(
            `VCollectionHeader=${collection}-${languageDirection}`,
            page.locator(".wrapper")
          )
        })
      }
    }
  })
})
