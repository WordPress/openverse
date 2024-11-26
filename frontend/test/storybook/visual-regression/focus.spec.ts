import { Page } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import { expectScreenshotAreaSnapshot } from "~~/test/playwright/utils/expect-snapshot"

const goTo = async (page: Page, slug: string) => {
  await page.goto(`/iframe.html?id=meta-focus--${slug}`)
}

const allSlugs = ["slim-transparent", "slim-filled", "bold-filled"]

test.describe.configure({ mode: "parallel" })

test.describe("Focus", () => {
  for (const slug of allSlugs) {
    test(`focus-${slug}`, async ({ page }) => {
      await goTo(page, slug)
      await page.focus('[data-testid="focus-target"]')

      await expectScreenshotAreaSnapshot(page, `focus-${slug}`)
    })
  }
})
