import { test } from "~~/test/playwright/utils/test"

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
        page.locator(wrapperLocator)
      )
    })

    test("hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").hover()
      await expectSnapshot(
        page,
        "v-load-more-hovered",
        page.locator(wrapperLocator)
      )
    })

    test("focused", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await expectSnapshot(
        page,
        "v-load-more-focused",
        page.locator(wrapperLocator)
      )
    })

    test("focused hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await page.getByRole("button").hover()
      await expectSnapshot(
        page,
        "v-load-more-focused-hovered",
        page.locator(wrapperLocator)
      )
    })
  })
})
