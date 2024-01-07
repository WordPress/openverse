import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

// Only used to isolate part of the Storybook frame;
// this shouldn't be used to reference this component in
// other E2E tests. Use a label or other visual property.
const safetyWallLocator = "#safety-wall"

test.describe.configure({ mode: "parallel" })

test.describe("VSafetyWall", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/iframe.html?id=components-vsafetywall--default-story")
  })

  breakpoints.describeEvery(({ expectSnapshot }) => {
    test("Renders the wall correctly for sensitive media", async ({ page }) => {
      await expectSnapshot(
        `v-safetywall-default`,
        page.locator(safetyWallLocator)
      )
    })
  })
})
