import { test, expect, Page } from "@playwright/test"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import {
  openAndCloseExternalLink,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { t } from "~~/test/playwright/utils/i18n"
import { getH1 } from "~~/test/playwright/utils/components"

const audioObject = {
  id: "1cb1af19-7232-40c2-b9ea-8d6c47e677f9",
  provider: "wikimedia_audio",
}
const goToCustomAudioPage = async (page: Page) => {
  // Test in a custom audio detail page, it should apply the same for any audio.
  await page.goto(`audio/${audioObject.id}`)
  await expect(getMainPlayButton(page)).toBeEnabled()
}

const errorPageHeading = (page: Page) => {
  return getH1(page, /The content you’re looking for seems to have disappeared/)
}
const getMainPlayButton = (page: Page) =>
  page.getByRole("button", { name: "Play" }).first()

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ page }) => {
  await preparePageForTests(page, "xl")
})

test("shows the data that is only available in single result, not search response", async ({
  page,
}) => {
  await goToCustomAudioPage(page)
  // Sample rate
  await expect(page.locator('dd:has-text("44100")')).toBeVisible()
})

test("sends GET_MEDIA event on CTA button click", async ({ context, page }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)
  await openAndCloseExternalLink(page, {
    name: new RegExp(t("audioDetails.weblink"), "i"),
  })

  const getMediaEvent = analyticsEvents.find((event) => event.n === "GET_MEDIA")

  expectEventPayloadToMatch(getMediaEvent, {
    ...audioObject,
    mediaType: "audio",
  })
})

test("sends AUDIO_INTERACTION event on play", async ({ page, context }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)

  await getMainPlayButton(page).click()

  const audioInteractionEvent = analyticsEvents.find(
    (event) => event.n === "AUDIO_INTERACTION"
  )

  expectEventPayloadToMatch(audioInteractionEvent, {
    ...audioObject,
    event: "play",
    component: "AudioDetailPage",
  })
})

test("sends AUDIO_INTERACTION event on seek", async ({ page, context }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)

  await page.mouse.click(200, 200)

  const audioInteractionEvent = analyticsEvents.find(
    (event) => event.n === "AUDIO_INTERACTION"
  )

  expectEventPayloadToMatch(audioInteractionEvent, {
    ...audioObject,
    event: "seek",
    component: "AudioDetailPage",
  })
})

test("shows the 404 error page when no valid id", async ({ page }) => {
  await page.goto("audio/foo")
  await expect(errorPageHeading(page)).toBeVisible()
})

test("shows the 404 error page when no id", async ({ page }) => {
  await page.goto("audio/")
  await expect(errorPageHeading(page)).toBeVisible()
})

test("sends SELECT_SEARCH_RESULT event on related audio click", async ({
  context,
  page,
}) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)

  // Clicking on the link seeks the audio, that's why we click on the heading
  const firstRelatedAudio = page
    .getByRole("region", { name: t("audioDetails.relatedAudios") })
    .locator("a")
    .first()
    .getByRole("heading", { level: 2 })

  await firstRelatedAudio.click()

  await page.waitForURL(/audio\/0b94484c-d7d1-43f2-8710-69399b6a0310/)

  const selectSearchResultEvent = analyticsEvents.find(
    (event) => event.n === "SELECT_SEARCH_RESULT"
  )

  expectEventPayloadToMatch(selectSearchResultEvent, {
    id: "0b94484c-d7d1-43f2-8710-69399b6a0310",
    relatedTo: audioObject.id,
    kind: "related",
    mediaType: "audio",
    provider: "wikimedia_audio",
    query: "",
    sensitivities: "",
    isBlurred: false,
    collectionType: null,
    collectionValue: null,
  })
})
