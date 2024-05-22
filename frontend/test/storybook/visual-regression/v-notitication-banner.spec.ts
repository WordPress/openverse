import { test } from "@playwright/test"

test.describe.configure({ mode: "parallel" })

import breakpoints from "~~/test/playwright/utils/breakpoints"

const natures = ["info", "warning", "error", "success"] as const
const variants = ["regular", "dark"] as const

const defaultUrl = "/iframe.html?id=components-vnotificationbanner--default"

const pageUrl = (
  nature: (typeof natures)[number],
  variant: (typeof variants)[number]
) => {
  const url = `${defaultUrl}&args=nature:${nature};variant:${variant}`
  return url
}

test.describe("VNotificationBanner", () => {
  for (const nature of natures) {
    for (const variant of variants) {
      breakpoints.describeMobileAndDesktop(({ expectSnapshot }) => {
        test(`notificationbanner-${nature}-${variant}`, async ({ page }) => {
          await page.goto(pageUrl(nature, variant))
          await expectSnapshot(
            `notificationbanner-${nature}-${variant}`,
            page.locator("section")
          )
        })
      })
    }
  }
})
