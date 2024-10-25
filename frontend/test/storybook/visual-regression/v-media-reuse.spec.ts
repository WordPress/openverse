import { test } from "~~/test/playwright/utils/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { sleep } from "~~/test/playwright/utils/navigation"
import { languageDirections, t } from "~~/test/playwright/utils/i18n"
import { dirParam } from "~~/test/storybook/utils/args"

test.describe.configure({ mode: "parallel" })

const tabs = [
  { id: "rich", name: "Rich Text" },
  { id: "html", name: "HTML" },
  { id: "plain", name: "Plain text" },
  { id: "xml", name: "XML" },
]
const defaultUrl = "/iframe.html?id=components-vmediainfo-vmediareuse--default"
const pageUrl = (dir: (typeof languageDirections)[number]) =>
  `${defaultUrl}${dirParam(dir)}`

test.describe("VMediaReuse", () => {
  for (const tab of tabs) {
    for (const dir of languageDirections) {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test(`should render a ${dir} media reuse section with "${tab.name}" tab open`, async ({
          page,
        }) => {
          await page.goto(pageUrl(dir))

          await page.locator(`#tab-${tab.id}`).click()
          // Make sure the tab is not focused and doesn't have a pink ring
          const reuseTitle = t("mediaDetails.reuse.title", dir)
          await page.locator(`h2:has-text("${reuseTitle}")`).click()
          await sleep(500)

          await expectSnapshot(
            page,
            `media-reuse-${tab.id}-tab-${dir}`,
            page.locator(".media-reuse")
          )
        })
      })
    }
  }
})
