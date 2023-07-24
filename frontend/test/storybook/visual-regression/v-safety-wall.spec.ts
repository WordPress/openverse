import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe("VSafetyWall", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/iframe.html?id=components-vsafetywall--default-story")
  })

  // breakpoints.describeEvery(({ expectSnapshot }) => {
  breakpoints.describeEvery(({}) => {
    test.fixme("todo", () => {
      // wow
    })
  })
})
