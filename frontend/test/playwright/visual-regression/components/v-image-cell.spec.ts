import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import { AspectRatio } from "~/types/media"

const imageLocator = "#VImageCell"
const imgLinkLocator = "VLink[itemprop='contentUrl']"
const imgElementLocator = "img[itemprop='thumbnailUrl']"

test.describe.configure({ mode: "parallel" })

test.describe("VImageCell", () => {
  const gotoWithArgs = makeGotoWithArgs("components-vimagecell--v-image-cell")
  const aspectRatios: AspectRatio[] = ["square", "4:3", "16:9"]

  for (const ratio of aspectRatios) {
    test(`${ratio} loaded`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      const imgElement = page.locator(imgElementLocator)
      await expect(imgElement).toBeVisible()
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-loaded.png`,
      })
    })

    test(`${ratio} on error`, async ({ page }) => {
      await gotoWithArgs(page, {
        aspectRatio: ratio,
        image: { url: "invalidUrl" },
      })
      const imgElement = page.locator(imgElementLocator)
      await page.waitForTimeout(2000) // Adjust timeout as necessary
      await expect(imgElement).toHaveAttribute(
        "src",
        "~/assets/image_not_available_placeholder.png"
      )
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-on-error.png`,
      })
    })

    test(`${ratio} focused`, async ({ page }) => {
      await gotoWithArgs(page, { aspectRatio: ratio })
      await page.focus(imgLinkLocator)
      expect(await page.locator(imageLocator).screenshot()).toMatchSnapshot({
        name: `v-image-cell-${ratio}-focused.png`,
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
