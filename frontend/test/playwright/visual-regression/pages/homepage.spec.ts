import { test } from "~~/test/playwright/utils/test-fixture"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  dismissTranslationBanner,
  dismissAnalyticsBanner,
  languageDirections,
  pathWithDir,
} from "~~/test/playwright/utils/navigation"

import type { Page } from "@playwright/test"

test.describe.configure({ mode: "parallel" })

/**
 * Make the random set of images uniform by dropping their brightness to zero,
 * and changing them into black circles.
 */
const cleanImageCarousel = async (page: Page) => {
  await page.addStyleTag({
    content: ".home-cell > img { filter: brightness(0%); }",
  })
  await page.waitForTimeout(1000) // wait for animation to finish
}

for (const dir of languageDirections) {
  test.describe(`${dir} homepage snapshots`, () => {
    const path = pathWithDir("/", dir)
    test.beforeEach(async ({ page }) => {
      await page.goto(path)
      await dismissTranslationBanner(page)
      await dismissAnalyticsBanner(page)
      await cleanImageCarousel(page)
      await page.mouse.move(0, 0)
    })

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test(`${dir} full page`, async ({ page }) => {
        await expectSnapshot(`index-${dir}`, page)
      })
    )

    test.describe("search input", () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test("unfocused", async ({ page }) => {
          await expectSnapshot(
            `unfocused-search-${dir}`,
            page.locator("form:has(input)")
          )
        })

        test("focused", async ({ page }) => {
          await page.focus("input")
          await hideInputCursors(page)
          await expectSnapshot(
            `focused-search-${dir}`,
            page.locator("form:has(input)")
          )
        })

        // @todo Fix flaky test: https://github.com/WordPress/openverse/issues/2377
        test.skip("content switcher open", async ({ page }) => {
          await page.locator("#search-type-button").click()

          await expectSnapshot(`content-switcher-open-${dir}`, page)
        })

        // @todo Fix flaky test: https://github.com/WordPress/openverse/issues/2377
        test.skip("content switcher with external sources open", async ({
          page,
        }) => {
          await page.goto(pathWithDir("/?ff_additional_search_types=on", dir))
          await cleanImageCarousel(page)

          await page.locator("#search-type-button").click()

          await expectSnapshot(
            `content-switcher-with-external-sources-open-${dir}`,
            page
          )
        })
      })
    })
  })
}
