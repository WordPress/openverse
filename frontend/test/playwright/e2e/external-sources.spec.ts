import { test } from "@playwright/test"

import { goToSearchTerm } from "~~/test/playwright/utils/navigation"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

test("sends correct analytics events", async ({ page, context }) => {
  const pagePromise = page.context().waitForEvent("page")

  const events = collectAnalyticsEvents(context)

  await goToSearchTerm(page, "cat", { mode: "SSR" })

  await page.getByRole("button", { name: "Source list" }).click()
  await page.getByRole("link", { name: "Centre for Ageing Better" }).click()

  const newPage = await pagePromise
  await newPage.close()

  const viewEvent = events.find((event) => event.n === "VIEW_EXTERNAL_SOURCES")
  const selectEvent = events.find(
    (event) => event.n === "SELECT_EXTERNAL_SOURCE"
  )

  expectEventPayloadToMatch(viewEvent, {
    searchType: "all",
    query: "cat",
    resultPage: 1,
  })
  expectEventPayloadToMatch(selectEvent, {
    name: "Centre For Ageing Better",
    mediaType: "image",
    query: "cat",
    component: "VExternalSourceList",
  })
})
