import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import type { AspectRatio } from "~/types/media"

const imageCell = "a[itemprop='contentUrl']"
// Necessary to make sure we can capture the focus state, which
// exceeds the bounds of the actual component
const screenshotEl = ".sb-main-padded"

test.describe.configure({ mode: "parallel" })

test.describe("VImageCell", () => {
  const gotoWithArgs = makeGotoWithArgs("components-vimagecell--v-image-cell")
  const aspectRatios: AspectRatio[] = ["square", "intrinsic"]

  for (const ratio of aspectRatios) {
    test(`${ratio} loaded`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      const mainEl = page.locator(imageCell)
      await expect(mainEl).toBeVisible()
      expect(await page.locator(screenshotEl).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-loaded.png`,
      })
    })

    test(`${ratio} focused`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imageCell)
      await page.locator(imageCell).click()
      expect(await page.locator(screenshotEl).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused.png`,
      })
    })

    test(`${ratio} hovered`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.hover(imageCell)
      expect(await page.locator(screenshotEl).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-hovered.png`,
      })
    })

    test(`${ratio} focused hovered`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imageCell)
      await page.hover(imageCell)
      await page.locator(imageCell).click()
      expect(await page.locator(screenshotEl).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused-hovered.png`,
      })
    })
  }
})
