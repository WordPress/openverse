import { test } from "@playwright/test"

import { openFirstResult } from "~~/test/playwright/utils/navigation"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import { AUDIO, IMAGE } from "~/constants/media"

test.describe("all results grid analytics test", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/search/?q=birds")
  })

  test("should send SELECT_SEARCH_RESULT event when audio result is selected", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)
    await openFirstResult(page, "audio")
    const selectSearchResultEvent = analyticsEvents.find(
      (event) => event.n === "SELECT_SEARCH_RESULT"
    )
    expectEventPayloadToMatch(selectSearchResultEvent, {
      mediaType: AUDIO,
      query: "birds",
      kind: "search",
      relatedTo: "null",
      id: "2e38ac1e-830c-4e9c-b13d-2c9a1ad53f95",
      provider: "jamendo",
      sensitivities: "",
      isBlurred: false,
    })
  })

  test("should send SELECT_SEARCH_RESULT event when image result is selected", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)
    await openFirstResult(page, "image")
    const selectSearchResultEvent = analyticsEvents.find(
      (event) => event.n === "SELECT_SEARCH_RESULT"
    )

    expectEventPayloadToMatch(selectSearchResultEvent, {
      id: "da5cb478-c093-4d62-b721-cda18797e3fb",
      kind: "search",
      mediaType: IMAGE,
      query: "birds",
      provider: "flickr",
      relatedTo: "null",
      sensitivities: "",
      isBlurred: false,
    })
  })

  test("should send AUDIO_INTERACTION event when audio is interacted", async ({
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(page.context())

    const firstResultPlay = page
      .locator(`a[href*="/audio/"]`)
      .first()
      .locator(`[aria-label="Play"]`)

    await firstResultPlay.click()

    const audioInteractionEvent = analyticsEvents.find(
      (event) => event.n === "AUDIO_INTERACTION"
    )

    expectEventPayloadToMatch(audioInteractionEvent, {
      id: "2e38ac1e-830c-4e9c-b13d-2c9a1ad53f95",
      event: "play",
      provider: "jamendo",
      component: "VAllResultsGrid",
    })
  })
})
