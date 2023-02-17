import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import { buttonVariants } from "~/types/button"

const buttonLocator = "text=Code is Poetry"

test.describe.configure({ mode: "parallel" })

test.describe("VButton", () => {
  const gotoWithArgs = makeGotoWithArgs("components-vbutton--v-button")
  const nonPressedVariants = buttonVariants.filter(
    (name) => !name.endsWith("pressed")
  )
  for (const variant of nonPressedVariants) {
    test(`${variant} resting`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      expect(await page.locator(buttonLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-resting.png`,
      })
    })

    test(`${variant} hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.hover(buttonLocator)
      expect(await page.locator(buttonLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-hovered.png`,
      })
    })

    test(`${variant} pressed`, async ({ page }) => {
      await gotoWithArgs(page, { variant, pressed: true })
      expect(await page.locator(buttonLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-pressed.png`,
      })
    })

    test(`${variant} pressed hovered`, async ({ page }) => {
      await gotoWithArgs(page, { variant })
      await page.hover(buttonLocator)
      expect(await page.locator(buttonLocator).screenshot()).toMatchSnapshot({
        name: `${variant}-pressed-hovered.png`,
      })
    })
    if (variant.startsWith("action")) {
      test(`${variant} disabled`, async ({ page }) => {
        await gotoWithArgs(page, { variant, disabled: true })
        expect(await page.locator(buttonLocator).screenshot()).toMatchSnapshot({
          name: `${variant}-disabled.png`,
        })
      })
    }
  }
})
