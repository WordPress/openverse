import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import type { AspectRatio } from "~/types/media"

const imageLocator = "ol.flex > li"
const imgLinkLocator = "a[itemprop='contentUrl']"
const imgElementLocator = "img[itemprop='thumbnailUrl']"

test.describe.configure({ mode: "parallel" })

test.describe("VImageCell", () => {
  const gotoWithArgs = makeGotoWithArgs("components-vimagecell--v-image-cell")
  const aspectRatios: AspectRatio[] = ["square", "intrinsic"]

  for (const ratio of aspectRatios) {
    test(`${ratio} loaded`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      const imgElement = page.locator(imgElementLocator)
      await expect(imgElement).toBeVisible()
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-loaded.png`,
      })
    })

    test(`${ratio} focused`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imgLinkLocator)
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused.png`,
      })
    })

    test(`${ratio} hovered`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imgLinkLocator)
      await page.hover(imgLinkLocator)
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused-hovered.png`,
      })
    })

    test(`${ratio} focused hovered`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imgLinkLocator)
      await page.hover(imgLinkLocator)
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused-hovered.png`,
      })
    })
  }
})
