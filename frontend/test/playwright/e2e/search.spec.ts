/**
 * Shows Search Grid / search meta information (count, etc.)
 * On clicking 'Load More', requests the same URL with the additional
 * `page=page+1` parameter
 * When finished, shows 'No more images'
 * When pending: does not show 'No images', Safer Browsing, search rating or error message
 * On error: shows error message
 */
import { expect, test } from "@playwright/test"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
  EventResponse,
} from "~~/test/playwright/utils/analytics"
import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  goToSearchTerm,
  preparePageForTests,
  scrollToBottom,
  searchFromHeader,
} from "~~/test/playwright/utils/navigation"
import { getH1 } from "~~/test/playwright/utils/components"

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
  await expect(getH1(page, /cat/i)).toBeVisible()

  scrollY = await page.evaluate(
    () => document.getElementById("main-page")?.scrollTop
  )

  expect(scrollY).toBe(0)
})

test("Send network errors to Plausible", async ({ context, page }) => {
  const analyticsEvents = collectAnalyticsEvents(context)
  await context.route(
    (url) => {
      // Only match the search requests, rather than any other API request the search page makes
      return Boolean(
        url.pathname.match(/v1\/(audio|images)/) &&
          url.searchParams.has("q", "galah")
      )
    },
    async (route) => route.abort("connectionaborted")
  )

  await goToSearchTerm(page, "galah", { mode: "CSR" })

  const searchErrorEvents = analyticsEvents.filter(
    (event) =>
      event.n === "NETWORK_ERROR" &&
      "requestKind" in event.p &&
      event.p.requestKind === "search"
  ) as EventResponse<"NETWORK_ERROR">[]
  expect(searchErrorEvents).toHaveLength(2)
  expectEventPayloadToMatch(
    searchErrorEvents.find((e) => e.p.searchType == "image"),
    { requestKind: "search", searchType: "image" }
  )
  expectEventPayloadToMatch(
    searchErrorEvents.find((e) => e.p.searchType == "audio"),
    { requestKind: "search", searchType: "audio" }
  )
})

test("Do not send network errors to Plausible when SSR", async ({
  context,
  page,
}) => {
  // Plausible not supported server-side, so skip sending the event
  const analyticsEvents = collectAnalyticsEvents(context)
  await context.route(
    (url) => {
      // Only match the search requests, rather than any other API request the search page makes
      return Boolean(
        url.pathname.match(/v1\/(audio|images)/) &&
          url.searchParams.has("q", "galah")
      )
    },
    async (route) => route.abort("connectionaborted")
  )

  await goToSearchTerm(page, "galah", { mode: "SSR" })

  const searchErrorEvents = analyticsEvents.filter(
    (event) =>
      event.n === "NETWORK_ERROR" &&
      "requestKind" in event.p &&
      event.p.requestKind === "search"
  ) as EventResponse<"NETWORK_ERROR">[]
  expect(searchErrorEvents).toHaveLength(0)
})

for (const renderMode of ["CSR", "SSR"] as const) {
  test(`Do not send non-network errors to Plausible - ${renderMode}`, async ({
    context,
    page,
  }) => {
    // This tests a _negative_, which isn't ideal, but seeing as we have tests for the error handling plugin, and the previous test,
    // `send errors to Plausible`, proves the plugin is being used (ignoring the possibility of conditionally calling the error
    // handling function), so there shouldn't be any network error events. Everything would get sent to Sentry, but we don't have a
    // way to assert Sentry requests in Playwright, so this approach will have to do.
    const analyticsEvents = collectAnalyticsEvents(context)
    await context.route(
      (url) => {
        // Only match the search requests, rather than any other API request the search page makes
        return Boolean(
          url.pathname.match(/v1\/(audio|images)/) &&
            url.searchParams.has("q", "galah")
        )
      },
      async (route) => {
        await route.fulfill({
          status: 500,
        })
      }
    )

    await goToSearchTerm(page, "galah", { mode: renderMode })

    const searchErrorEvents = analyticsEvents.filter(
      (event) => event.n === "NETWORK_ERROR"
    ) as EventResponse<"NETWORK_ERROR">[]
    expect(searchErrorEvents).toHaveLength(0)
  })
}
