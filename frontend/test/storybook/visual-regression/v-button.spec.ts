import { test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

import { buttonVariants } from "~/types/button"

const buttonLocator = "text=Code is Poetry"
const wrapperLocator = "#wrapper"

test.describe.configure({ mode: "parallel" })

test.describe("VButton", () => {
  const gotoWithArgs = makeGotoWithArgs("components-vbutton--default")
  const nonPressedVariants = buttonVariants.filter(
    (name) => !name.endsWith("pressed")
  )
  for (const variant of nonPressedVariants) {
    test(`${variant} resting`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await expectSnapshot(`${variant}-resting`, page.locator(wrapperLocator))
    })

    test(`${variant} hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.hover(buttonLocator)
      await expectSnapshot(`${variant}-hovered`, page.locator(wrapperLocator))
    })

    test(`${variant} focused`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.focus(buttonLocator)
      await expectSnapshot(`${variant}-focused`, page.locator(wrapperLocator))
    })

    test(`${variant} focused hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.focus(buttonLocator)
      await page.hover(buttonLocator)
      await expectSnapshot(
        `${variant}-focused-hovered`,
        page.locator(wrapperLocator)
      )
    })
  }
})
