import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

test.describe("VCollectionHeader", () => {
  breakpoints.describeEvery(({ expectSnapshot }) => {
    for (const languageDirection of ["ltr", "rtl"]) {
      test(`All headers ${languageDirection}`, async ({ page }) => {
        await page.goto(
          `/iframe.html?id=components-vcollectionheader--all-collections`
        )
        await expectSnapshot(
          `VCollectionHeaders-${languageDirection}`,
          page.locator(".wrapper")
        )
      })
    }
  })
})
