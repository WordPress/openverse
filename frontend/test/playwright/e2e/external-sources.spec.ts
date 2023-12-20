import { test } from "@playwright/test"

import {
  goToSearchTerm,
  t,
  turnOnAnalytics,
} from "~~/test/playwright/utils/navigation"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

test("sends VIEW_EXTERNAL_SOURCES analytics events", async ({
  page,
  context,
}) => {
  await turnOnAnalytics(page)
  const events = collectAnalyticsEvents(context)

  await goToSearchTerm(page, "cat", { searchType: "image", mode: "SSR" })

  await page
    .getByRole("button", { name: t("externalSources.form.supportedTitle") })
    .click()
  await page.getByRole("button", { name: /close/i }).click()

  const viewEvent = events.find((event) => event.n === "VIEW_EXTERNAL_SOURCES")

  expectEventPayloadToMatch(viewEvent, {
    searchType: "image",
    query: "cat",
    resultPage: 1,
  })
})

test("sends SELECT_EXTERNAL_SOURCE analytics events", async ({
  page,
  context,
}) => {
  await turnOnAnalytics(page)
  const pagePromise = page.context().waitForEvent("page")

  const events = collectAnalyticsEvents(context)

  await goToSearchTerm(page, "cat", { searchType: "image", mode: "SSR" })

  await page
    .getByRole("button", {
      name: new RegExp(t("externalSources.form.supportedTitleSm"), "i"),
    })
    .click()
  await page.getByRole("link", { name: "Centre for Ageing Better" }).click()

  const newPage = await pagePromise
  await newPage.close()

  const selectEvent = events.find(
    (event) => event.n === "SELECT_EXTERNAL_SOURCE"
  )

  expectEventPayloadToMatch(selectEvent, {
    name: "Centre For Ageing Better",
    mediaType: "image",
    query: "cat",
    component: "VExternalSourceList",
  })
})
