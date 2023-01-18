import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { removeHiddenOverflow } from "~~/test/playwright/utils/page"
import {
  pathWithDir,
  languageDirections,
  setCookies,
  enableOldHeader,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const contentPages = ["about", "search-help", "non-existent", "sources"]
for (const contentPage of contentPages) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test("full page", async ({ context, page }) => {
          await enableOldHeader(page)
          await setCookies(context, {
            uiBreakpoint: breakpoint,
            uiDismissedBanners: ["translation-ar"],
          })

          await page.goto(pathWithDir(contentPage, dir))

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
