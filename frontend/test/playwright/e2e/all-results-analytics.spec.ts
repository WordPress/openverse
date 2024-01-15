import { expect, test } from "@playwright/test"

import {
  goToSearchTerm,
  openFirstResult,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import { t } from "~~/test/playwright/utils/i18n"

import { AUDIO, IMAGE } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

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
    expectEventPayloadToMatch(selectSearchResultEvent, {
      mediaType: AUDIO,
      query: "birds",
      kind: "search",
      relatedTo: null,
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
      relatedTo: null,
      sensitivities: "",
      isBlurred: false,
    })
  })

  test("sends AUDIO_INTERACTION event when audio is interacted", async ({
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(page.context())

    const firstResultPlay = page
      .locator(`a[href*="/audio/"]`)
      .first()
      .getByRole("button", { name: /play/i })

    await firstResultPlay.click()
    await expect(page.getByRole("button", { name: /pause/i })).toBeVisible()

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

    expectEventPayloadToMatch(changeContentTypeEvent, {
      component: "VContentLink",
      next: "image",
      previous: "all",
    })
  })
})
