/**
 * Shows Search Grid / search meta information (count, etc.)
 * On clicking 'Load More', requests the same URL with the additional
 * `page=page+1` parameter
 * When finished, shows 'No more images'
 * When pending: does not show 'No images', Safer Browsing, search rating or error message
 * On error: shows error message
 */
import { expect, test } from "@playwright/test"

import { API_URL } from "~~/test/playwright/playwright.config"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  goToSearchTerm,
  preparePageForTests,
  scrollToBottom,
  searchFromHeader,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ context, page }) => {
  await preparePageForTests(page, "xl")
  await mockProviderApis(context)
})

test("scroll to top on new search term submitted", async ({ page }) => {
  await goToSearchTerm(page, "galah")
  await scrollToBottom(page)

  let scrollY = await page.evaluate(
    () => document.getElementById("main-page")?.scrollTop
  )

  expect(scrollY).not.toBe(0)

  await searchFromHeader(page, "cat")
  scrollY = await page.evaluate(
    () => document.getElementById("main-page")?.scrollTop
  )

  expect(scrollY).toBe(0)
})

test("Ignore network errors", async ({ context, page }) => {
  const analyticsEvents = collectAnalyticsEvents(context)
  await context.route(/\/v1\/(images|audio)\//, (route) =>
    route.abort("connectionaborted")
  )

  await goToSearchTerm(page, "galah", { mode: "CSR" })

  const networkErrorEvent = analyticsEvents.find(
    (event) => event.n === "NETWORK_ERROR"
  )
  expectEventPayloadToMatch(networkErrorEvent, {
    requestKind: "single-result",
    searchType: "all",
  })
})
