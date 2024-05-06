import { expect, Page, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import type { AspectRatio } from "~/types/media"

const imageCell = "a[itemprop='contentUrl']"
const imageCellImage = `${imageCell} img`
// Necessary to make sure we can capture the focus state, which
// exceeds the bounds of the actual component
const screenshotEl = ".sb-main-padded"

test.describe.configure({ mode: "parallel" })

const gotoWithArgs = makeGotoWithArgs("components-vimagecell--v-image-cell")

const goAndWaitForImage = async (
  page: Page,
  args: Record<string, string | number | boolean>
) => {
  const responsePromise = page.waitForResponse((resp) =>
    resp.request().url().endsWith(".jpg")
  )
  await gotoWithArgs(page, args)
  await responsePromise
  await expect(page.locator(imageCellImage)).toBeVisible()
}

test.describe("VImageCell", () => {
  breakpoints.describeMobileXsAndDesktop(({ expectSnapshot }) => {
    const aspectRatios: AspectRatio[] = ["square", "intrinsic"]

    for (const ratio of aspectRatios) {
      test(`${ratio} loaded`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        const mainEl = page.locator(imageCell)
        await expect(mainEl).toBeVisible()

        await expectSnapshot(
          `v-image-cell-${ratio}-loaded`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused`, async ({ page }) => {
        await goAndWaitForImage(page, { aspectRatio: ratio })

        await page.focus(imageCell)
        await page.locator(imageCell).click()

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
