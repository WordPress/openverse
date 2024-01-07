import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { sleep } from "~~/test/playwright/utils/navigation"

import type { AspectRatio } from "~/types/media"

const imageCell = "a[itemprop='contentUrl']"
// Necessary to make sure we can capture the focus state, which
// exceeds the bounds of the actual component
const screenshotEl = ".sb-main-padded"

test.describe.configure({ mode: "parallel" })

test.describe("VImageCell", () => {
  breakpoints.describeMobileXsAndDesktop(({ expectSnapshot }) => {
    const gotoWithArgs = makeGotoWithArgs("components-vimagecell--v-image-cell")
    const aspectRatios: AspectRatio[] = ["square", "intrinsic"]

    for (const ratio of aspectRatios) {
      test(`${ratio} loaded`, async ({ page }) => {
        await gotoWithArgs(page, { aspectRatio: ratio })

        await sleep(500)
        const mainEl = page.locator(imageCell)
        await expect(mainEl).toBeVisible()
        await expectSnapshot(
          `v-image-cell-${ratio}-loaded`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused`, async ({ page }) => {
        await gotoWithArgs(page, { aspectRatio: ratio })
        await sleep(500)

        await page.focus(imageCell)
        await page.locator(imageCell).click()
        await expectSnapshot(
          `v-image-cell-${ratio}-focused`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} hovered`, async ({ page }) => {
        await gotoWithArgs(page, { aspectRatio: ratio })
        await sleep(500)

        await page.hover(imageCell)
        await expectSnapshot(
          `v-image-cell-${ratio}-hovered`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused hovered`, async ({ page }) => {
        await gotoWithArgs(page, { aspectRatio: ratio })
        await sleep(500)

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
