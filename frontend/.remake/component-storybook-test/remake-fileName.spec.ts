import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe("<%= name %>", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(
      "/iframe.html?id=components-<%= name.toLowerCase() %>--default-story"
    )
  })

  breakpoints.describeEvery(({ expectSnapshot }) => {})
})
