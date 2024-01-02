import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { languageDirections, t } from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const tabs = [
  { id: "rich", name: "Rich Text" },
  { id: "html", name: "HTML" },
  { id: "plain", name: "Plain text" },
]
const defaultUrl =
  "/iframe.html?id=components-vmediainfo-vmediareuse--v-media-reuse"
const pageUrl = (dir: (typeof languageDirections)[number]) =>
  dir === "ltr" ? defaultUrl : `${defaultUrl}&globals=languageDirection:rtl`

test.describe("VMediaReuse", () => {
  for (const tab of tabs) {
    for (const dir of languageDirections) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test.beforeEach(async ({ page }) => {
          await page.goto(pageUrl(dir))
          if (dir === "rtl") {
            await page.locator("#language").selectOption({ value: "ar" })
          }
        })

        test(`Should render a ${dir} media reuse section with "${tab.name}" tab open`, async ({
          page,
        }) => {
          await page.locator(`#tab-${tab.id}`).click()
          // Make sure the tab is not focused and doesn't have a pink ring
          const reuseTitle = t("mediaDetails.reuse.title", dir)
          await page.locator(`h2:has-text("${reuseTitle}")`).click()
          await expectSnapshot(
            `media-reuse-${dir}-${tab.id}-tab`,
            page.locator(".media-reuse")
          )
        })
      })
    }
  }
})
