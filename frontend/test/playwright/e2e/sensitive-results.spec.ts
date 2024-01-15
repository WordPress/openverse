import { expect, Page, test } from "@playwright/test"

import {
  filters,
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { t } from "~~/test/playwright/utils/i18n"
import { getH1, getHomeLink } from "~~/test/playwright/utils/components"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

test.describe.configure({ mode: "parallel" })

const getSensitiveToggle = (page: Page) => {
  return page.getByRole("checkbox", {
    name: t("filters.safeBrowsing.toggles.fetchSensitive.title"),
  })
}
const getFirstSensitiveResult = (page: Page) => {
  return page
    .getByRole("link", {
      name: /This image may contain sensitive content/i,
    })
    .first()
}

test.describe("sensitive_results", () => {
  test.afterEach(async ({ context }) => {
    await context.clearCookies()
  })

  test("can set `includeSensitiveResults` filter by toggling the UI", async ({
    page,
  }) => {
    await preparePageForTests(page, "xl", {
      features: { fake_sensitive: "on" },
    })
    await goToSearchTerm(page, "cat", { mode: "CSR" })

    // Check the sensitive toggle on a search page
    await filters.open(page)
    await getSensitiveToggle(page).click()

    // Search from the home page
    await getHomeLink(page).click()
    await page.locator('main input[type="search"]').fill("cat")
    await page.keyboard.press("Enter")

    // Check the sensitive media on the search page
    await expect(getH1(page, /cat/i)).toBeVisible()
    const sensitiveImageLink = getFirstSensitiveResult(page)
    await expect(sensitiveImageLink).toBeVisible()
  })

  test("sends UNBLUR_SENSITIVE_RESULT", async ({ page, context }) => {
    await preparePageForTests(page, "xl", {
      features: { fake_sensitive: "on", fetch_sensitive: "on" },
    })
    const analyticsEvents = collectAnalyticsEvents(context)
    await goToSearchTerm(page, "cat")
    await getFirstSensitiveResult(page).click()

    await page.getByRole("button", { name: /show content/i }).click()

    const unblurSensitiveResultEvent = analyticsEvents.find(
      (event) => event.n === "UNBLUR_SENSITIVE_RESULT"
    )
    expectEventPayloadToMatch(unblurSensitiveResultEvent, {
      id: "de42d499-d660-47b4-b203-28d5589c31d2",
      sensitivities: "user_reported_sensitive",
    })
  })

  test("sends REBLUR_SENSITIVE_RESULT", async ({ page, context }) => {
    await preparePageForTests(page, "xl", {
      features: { fake_sensitive: "on", fetch_sensitive: "on" },
    })
    const analyticsEvents = collectAnalyticsEvents(context)
    await goToSearchTerm(page, "cat")
    await getFirstSensitiveResult(page).click()

    await page.getByRole("button", { name: /show content/i }).click()
    await page.getByRole("button", { name: /hide content/i }).click()

    const reblurSensitiveResultEvent = analyticsEvents.find(
      (event) => event.n === "REBLUR_SENSITIVE_RESULT"
    )
    expectEventPayloadToMatch(reblurSensitiveResultEvent, {
      id: "de42d499-d660-47b4-b203-28d5589c31d2",
      sensitivities: "user_reported_sensitive",
    })
  })
})
