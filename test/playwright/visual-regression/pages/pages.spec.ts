import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { removeHiddenOverflow } from "~~/test/playwright/utils/page"
import {
  pathWithDir,
  languageDirections,
  enableNewHeader,
  setCookies,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const contentPages = [
  "about",
  "privacy",
  "search-help",
  "non-existent",
  "sources",
]
for (const contentPage of contentPages) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test.beforeEach(async ({ context, page }) => {
          await enableNewHeader(page)
          await setCookies(context, {
            uiBreakpoint: breakpoint as string,
            uiIsFilterDismissed: true,
            uiDismissedBanners: ["translation-ar"],
          })
          await page.goto(pathWithDir(contentPage, dir))
        })

        test("full page", async ({ page }) => {
          await removeHiddenOverflow(page)
          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await expectSnapshot(`${contentPage}-${dir}`, page, {
            fullPage: true,
          })
        })
      })
    })
  }
}
