import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import {
  getFirstResult,
  goToSearchTerm,
  openFirstResult,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import { t } from "~~/test/playwright/utils/i18n"

import { ALL_MEDIA, AUDIO, IMAGE } from "#shared/constants/media"
import type { Events } from "#shared/types/analytics"

test.describe.configure({ mode: "parallel" })

const searchResultPayload = {
  kind: "search",
  collectionType: "null",
  searchType: ALL_MEDIA,
} as const

const defaultPayload = {
  ...searchResultPayload,
  isBlurred: false,
  relatedTo: "null",
  sensitivities: "",
} as const

const audioResult = {
  mediaType: AUDIO,
  id: "2e38ac1e-830c-4e9c-b13d-2c9a1ad53f95",
  provider: "jamendo",
} as const

test.describe("all results grid analytics test", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
    await goToSearchTerm(page, "birds")
  })

  test("sends SELECT_SEARCH_RESULT event when audio result is selected", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await openFirstResult(page, "audio")
    const selectSearchResultEvent = analyticsEvents.find(
      (event) => event.n === "SELECT_SEARCH_RESULT"
    )
    const expectedPayload: Events["SELECT_SEARCH_RESULT"] = {
      ...defaultPayload,
      ...audioResult,
    }
    expectEventPayloadToMatch(selectSearchResultEvent, expectedPayload)
  })

  test("sends SELECT_SEARCH_RESULT event when image result is selected", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await openFirstResult(page, "image")
    const selectSearchResultEvent = analyticsEvents.find(
      (event) => event.n === "SELECT_SEARCH_RESULT"
    )
    const expectedPayload: Events["SELECT_SEARCH_RESULT"] = {
      ...defaultPayload,
      id: "da5cb478-c093-4d62-b721-cda18797e3fb",
      mediaType: IMAGE,
      provider: "flickr",
    }

    expectEventPayloadToMatch(selectSearchResultEvent, expectedPayload)
  })

  test("sends AUDIO_INTERACTION event when audio is interacted", async ({
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(page.context())

    const firstResult = await getFirstResult(page, "audio")

    const firstResultPlay = firstResult.getByRole("button", { name: /play/i })

    await firstResultPlay.click()
    await expect(page.getByRole("button", { name: /pause/i })).toBeVisible()

    const audioInteractionEvent = analyticsEvents.find(
      (event) => event.n === "AUDIO_INTERACTION"
    )
    const expectedPayload: Events["AUDIO_INTERACTION"] = {
      id: audioResult.id,
      provider: audioResult.provider,
      event: "play",
      component: "VAllResultsGrid",
    }
    expectEventPayloadToMatch(audioInteractionEvent, expectedPayload)
  })

  test("sends CHANGE_CONTENT_TYPE event when content type is changed", async ({
    page,
    context,
  }) => {
    const events = collectAnalyticsEvents(context)

    await page.getByRole("link", { name: /see .+ images found for/i }).click()
    // Make sure the navigation is done by checking for external sources form
    await expect(
      page.getByRole("button", {
        name: new RegExp(t("externalSources.form.supportedTitleSm"), "i"),
      })
    ).toBeVisible()

    const changeContentTypeEvent = events.find(
      (event) => event.n === "CHANGE_CONTENT_TYPE"
    )
    const expectedPayload: Events["CHANGE_CONTENT_TYPE"] = {
      component: "VContentLink",
      next: "image",
      previous: "all",
    }
    expectEventPayloadToMatch(changeContentTypeEvent, expectedPayload)
  })
})
