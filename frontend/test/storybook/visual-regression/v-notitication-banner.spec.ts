import { test } from "~~/test/playwright/utils/test"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

const natures = ["info", "warning", "error", "success"] as const
const variants = ["regular", "dark"] as const

const defaultUrl = "/iframe.html?id=components-vnotificationbanner--default"

const pageUrl = (
  nature: (typeof natures)[number],
  variant: (typeof variants)[number]
) => {
  return `${defaultUrl}&args=nature:${nature};variant:${variant}`
}

test.describe("VNotificationBanner", () => {
  for (const nature of natures) {
    for (const variant of variants) {
      breakpoints.describeMobileAndDesktop(({ expectSnapshot }) => {
        test(`notificationbanner-${nature}-${variant}`, async ({ page }) => {
          await page.goto(pageUrl(nature, variant))
          await expectSnapshot(
            page,
            `notificationbanner-${nature}-${variant}`,
            page.locator("section")
          )
        })
      })
    }
  }
})
