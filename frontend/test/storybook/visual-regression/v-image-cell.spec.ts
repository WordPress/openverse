import { expect, type Page, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { makeUrlWithArgs } from "~~/test/storybook/utils/args"
import { sleep } from "~~/test/playwright/utils/navigation"
import { waitForResponse } from "~~/test/storybook/utils/response"

import type { AspectRatio } from "~/types/media"

const imageCell = "a[itemprop='contentUrl']"
const imageCellImage = `${imageCell} img`
// Necessary to make sure we can capture the focus state, which
// exceeds the bounds of the actual component
const screenshotEl = ".sb-main-padded"

const urlWithArgs = makeUrlWithArgs("components-vimagecell--default")

const goAndWaitForImage = async (
  page: Page,
  args: Record<string, string | number | boolean>
) => {
  // Block the flickr direct url request so that the image cell immediately
  // falls back to the local image.
  await page.route("**flickr**", (route) => route.abort())
  await waitForResponse(page, urlWithArgs(args), /\.jpg/)
  await expect(page.locator(imageCellImage)).toBeVisible()
  await sleep(500)
}

test.describe.configure({ mode: "parallel" })

test.describe("VImageCell", () => {
  breakpoints.describeMobileXsAndDesktop(({ expectSnapshot }) => {
    const aspectRatios: AspectRatio[] = ["square", "intrinsic"]

    for (const ratio of aspectRatios) {
      test(`${ratio} loaded`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        await expectSnapshot(
          `v-image-cell-${ratio}-loaded`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        await page.focus(imageCell)

        await expectSnapshot(
          `v-image-cell-${ratio}-focused`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} hovered`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        await page.hover(imageCell)

        await expectSnapshot(
          `v-image-cell-${ratio}-hovered`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused hovered`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        await page.focus(imageCell)
        await page.hover(imageCell)
        await page.locator(imageCell).click()

        await expectSnapshot(
          `v-image-cell-${ratio}-focused-hovered`,
          page.locator(screenshotEl)
        )
      })
    }
  })
})
