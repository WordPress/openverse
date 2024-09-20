import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { makeUrlWithArgs } from "~~/test/storybook/utils/args"

import type { AspectRatio } from "~/types/media"

const imageCell = "a[itemprop='contentUrl']"

// Necessary to make sure we can capture the focus state, which
// exceeds the bounds of the actual component
const screenshotEl = ".image-wrapper"

const urlWithArgs = makeUrlWithArgs("components-vimagecell--default")

test.describe.configure({ mode: "parallel" })

const aspectRatios: AspectRatio[] = ["square", "intrinsic"]
test.describe("VImageCell", () => {
  breakpoints.describeMobileXsAndDesktop(({ expectSnapshot }) => {
    for (const ratio of aspectRatios) {
      test.beforeEach(async ({ page }) => {
        await page.routeFromHAR("./test/hars/v-image-cell.har", {
          url: /\/thumb\//,
        })
      })

      test(`${ratio} loaded`, async ({ page }) => {
        await page.goto(urlWithArgs({ aspectRatio: ratio }))
        await expectSnapshot(
          page,
          `v-image-cell-${ratio}-loaded`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused`, async ({ page }) => {
        await page.goto(urlWithArgs({ aspectRatio: ratio }))

        await page.focus(imageCell)

        await expectSnapshot(
          page,
          `v-image-cell-${ratio}-focused`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} hovered`, async ({ page }) => {
        await page.goto(urlWithArgs({ aspectRatio: ratio }))

        await page.hover(imageCell)

        await expectSnapshot(
          page,
          `v-image-cell-${ratio}-hovered`,
          page.locator(screenshotEl)
        )
      })

      test(`${ratio} focused hovered`, async ({ page }) => {
        await page.goto(urlWithArgs({ aspectRatio: ratio }))

        await page.focus(imageCell)
        await page.hover(imageCell)
        await page.locator(imageCell).click()

        await expectSnapshot(
          page,
          `v-image-cell-${ratio}-focused-hovered`,
          page.locator(screenshotEl)
        )
      })
    }
  })
})
