import { test, Page } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  languageDirections,
  pathWithDir,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

/**
 * Make the random set of images uniform by dropping their brightness to zero,
 * and changing them into black circles.
 */
const cleanImageCarousel = async (page: Page) => {
  await page.addStyleTag({
    content: ".home-cell > img { filter: brightness(0%); }",
  })
  // wait for animation to finish
  // eslint-disable-next-line playwright/no-wait-for-timeout
  await page.waitForTimeout(1000)
}

for (const dir of languageDirections) {
  const path = pathWithDir("/", dir)

  breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
    test.describe(`${dir} homepage`, () => {
      test.beforeEach(async ({ page }) => {
        await preparePageForTests(page, breakpoint, {
          features: { additional_search_types: "off" },
        })
        await page.goto(path)
        await cleanImageCarousel(page)
        await page.mouse.move(0, 0)
      })

      test(`${dir} full page`, async ({ page }) => {
        await expectSnapshot(`index-${dir}`, page)
      })

      test.describe("search input", () => {
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

        test("content switcher open", async ({ page }) => {
          await page.locator("#search-type-button").click()

          await expectSnapshot(`content-switcher-open-${dir}`, page)
        })

        test("content switcher with external sources open", async ({
          page,
        }) => {
          await preparePageForTests(page, breakpoint, {
            features: { additional_search_types: "on" },
          })

          await page.goto(path)
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
