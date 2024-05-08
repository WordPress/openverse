import { test, Page } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

const goTo = async (page: Page, slug: string) => {
  await page.goto(`/iframe.html?id=components-vmedialicense--${slug}`)
}

/**
 * parts of Storybook's story IDs for VMediaLicense stories; Note that these are
 * distinct from license slugs such as 'cc0' (changed to 'cc-0' here) and
 * 'sampling+' (changed to 'cc-sampling' here).
 */
const allSlugs = [
  "cc-by",
  "cc-by-sa",
  "cc-by-nd",
  "cc-by-nc",
  "cc-by-nc-sa",
  "cc-by-nc-nd",
  "cc-0",
  "pdm",
  "sampling",
  "nc-sampling",
]
test.describe.configure({ mode: "parallel" })

test.describe("VMediaLicense", () => {
  for (const slug of allSlugs) {
    const name = `v-media-license-${slug}`
    breakpoints.describeMobileAndDesktop(({ expectSnapshot }) => {
      test(name, async ({ page }) => {
        await goTo(page, slug)
        await expectSnapshot(name, page.locator(".media-attribution"))
      })
    })
  }
})
