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
      await expectSnapshot("v-load-more-resting", page.locator(wrapperLocator))
    })

    test("hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").hover()
      await expectSnapshot("v-load-more-hovered", page.locator(wrapperLocator))
    })

    test("focused", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await expectSnapshot("v-load-more-focused", page.locator(wrapperLocator))
    })

    test("focused hovered", async ({ page }) => {
      await gotoWithArgs(page)
      await page.getByRole("button").focus()
      await page.getByRole("button").hover()
      await expectSnapshot(
        "v-load-more-focused-hovered",
        page.locator(wrapperLocator)
      )
    })
  })
})
