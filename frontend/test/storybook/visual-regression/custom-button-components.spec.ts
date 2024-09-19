import { test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"
import breakpoints from "~~/test/playwright/utils/breakpoints"

const wrapperLocator = "#wrapper"

test.describe.configure({ mode: "parallel" })

test.describe("VLoadMore button", () => {
  const gotoWithArgs = makeGotoWithArgs(
    "components-custombuttoncomponents--default"
  )
  breakpoints.describeMobileAndDesktop(({ expectSnapshot }) => {
    test("resting", async ({ page }) => {
      await gotoWithArgs(page)
      await expectSnapshot(
        page,
        "v-load-more-resting",
        page.locator(wrapperLocator),
        { snapshotOptions: { maxDiffPixelRatio: 0 } }
      )
    })

    test("hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").hover()
      await expectSnapshot(
        page,
        "v-load-more-hovered",
        page.locator(wrapperLocator),
        { snapshotOptions: { maxDiffPixelRatio: 0 } }
      )
    })

    test("focused", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await expectSnapshot(
        page,
        "v-load-more-focused",
        page.locator(wrapperLocator),
        { snapshotOptions: { maxDiffPixelRatio: 0 } }
      )
    })

    test("focused hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await page.getByRole("button").hover()
      await expectSnapshot(
        page,
        "v-load-more-focused-hovered",
        page.locator(wrapperLocator),
        { snapshotOptions: { maxDiffPixelRatio: 0 } }
      )
    })
  })
})
