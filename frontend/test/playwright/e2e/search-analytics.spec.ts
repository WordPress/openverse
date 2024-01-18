import { expect, test } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
  searchFromHeader,
} from "~~/test/playwright/utils/navigation"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import { ALL_MEDIA, IMAGE } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

test.describe("standalone searchbar", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
  })

  test("sends SUBMIT_SEARCH event from the homepage", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat", { mode: "CSR", searchType: IMAGE })

    const searchEvent = analyticsEvents.find(
      (event) => event.n === "SUBMIT_SEARCH"
    )

    expectEventPayloadToMatch(searchEvent, {
      searchType: IMAGE,
      query: "cat",
    })
  })

  test("sends SUBMIT_SEARCH event from the full-page error", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await page.goto("/error-page")

    await expect(page.getByRole("button", { name: /search/i })).toBeEnabled()
    await page.locator("#search-bar").fill("cat")
    await page.keyboard.press("Enter")

    await page.waitForURL(/search/)

    const searchEvent = analyticsEvents.find(
      (event) => event.n === "SUBMIT_SEARCH"
    )

    expectEventPayloadToMatch(searchEvent, {
      searchType: ALL_MEDIA,
      query: "cat",
    })
  })
})

test.describe("search page searchbar", () => {
  test("sends SUBMIT_SEARCH event from the search page header searchbar", async ({
    context,
    page,
  }) => {
    await preparePageForTests(page, "xl")
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat", { mode: "CSR" })

    await searchFromHeader(page, "birds")

    const searchEvent = analyticsEvents.filter(
      (event) => event.n === "SUBMIT_SEARCH"
    )

    expect(searchEvent.length).toBe(2)
    expectEventPayloadToMatch(searchEvent[1], {
      searchType: ALL_MEDIA,
      query: "birds",
    })
  })
})
