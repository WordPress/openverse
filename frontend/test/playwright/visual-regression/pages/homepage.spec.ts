import { Page } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  pathWithDir,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { languageDirections } from "~~/test/playwright/utils/i18n"

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

      test("full page", async ({ page }) => {
        await expectSnapshot(page, "index", page, { dir })
      })

      test.describe("search input", () => {
        test("unfocused", async ({ page }) => {
          await expectSnapshot(
            page,
            `unfocused-search`,
            page.locator("form:has(input)"),
            { dir }
          )
        })

        test("focused", async ({ page }) => {
          await page.focus("input")
          await hideInputCursors(page)
          await expectSnapshot(
            page,
            "focused-search",
            page.locator("form:has(input)"),
            { dir }
          )
        })

        test("content switcher open", async ({ page }) => {
          await page.locator("#search-type-button").click()
          // eslint-disable-next-line playwright/no-conditional-in-test
          if (["lg", "xl", "2xl"].includes("breakpoint")) {
            await page.locator("#search-type-button").hover()
          }

          await expectSnapshot(page, "content-switcher-open", page, { dir })
        })
      })
    })

    test(`${dir} content switcher with additional search types open`, async ({
      page,
    }) => {
      await preparePageForTests(page, breakpoint, {
        features: { additional_search_types: "on" },
      })

      await page.goto(path)
      await cleanImageCarousel(page)

      await page.locator("#search-type-button").click()

      await expectSnapshot(
        page,
        "content-switcher-with-external-sources-open",
        page,
        { dir }
      )
    })
  })
}
