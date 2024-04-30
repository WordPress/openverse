import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

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
      expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-resting.png`,
      })
    })

    test(`${variant} hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.hover(buttonLocator)
      expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-hovered.png`,
      })
    })

    test(`${variant} focused`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.focus(buttonLocator)
      expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-focused.png`,
      })
    })

    test(`${variant} focused hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.focus(buttonLocator)
      await page.hover(buttonLocator)
      expect(await page.locator(wrapperLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-focused-hovered.png`,
      })
    })
  }
})
