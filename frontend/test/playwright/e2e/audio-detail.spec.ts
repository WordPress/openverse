import { test, expect, Page } from "@playwright/test"

import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

const goToCustomAudioPage = async (page: Page) => {
  // Test in a custom audio detail page, it should apply the same for any audio.
  await page.goto("audio/7e063ee6-343f-48e4-a4a5-f436393730f6")
}

const showsErrorPage = async (page: Page) => {
  await expect(page.locator("h1")).toHaveText(
    /The content you’re looking for seems to have disappeared/
  )
}

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

test("shows the data that is only available in single result, not search response", async ({
  page,
}) => {
  await goToCustomAudioPage(page)
  await expect(
    page.locator('dd:has-text("I Love My Dog You Love Your Cat")')
  ).toBeVisible()
})

test("sends a custom event on play", async ({ page, context }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)
  await page.getByRole("button", { name: "Play" }).first().click()
  const audioInteractionEvent = analyticsEvents.find(
    (event) => event.n === "AUDIO_INTERACTION"
  )

  expectEventPayloadToMatch(audioInteractionEvent, {
    id: "7e063ee6-343f-48e4-a4a5-f436393730f6",
    event: "play",
    provider: "jamendo",
    component: "AudioDetailPage",
  })
})

test("sends a custom event on seek", async ({ page, context }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomAudioPage(page)
  await page.mouse.click(200, 200)
  const audioInteractionEvent = analyticsEvents.find(
    (event) => event.n === "AUDIO_INTERACTION"
  )

  expectEventPayloadToMatch(audioInteractionEvent, {
    id: "7e063ee6-343f-48e4-a4a5-f436393730f6",
    event: "seek",
    provider: "jamendo",
    component: "AudioDetailPage",
  })
})

test("shows the 404 error page when no valid id", async ({ page }) => {
  await page.goto("audio/foo")
  await showsErrorPage(page)
})

test("shows the 404 error page when no id", async ({ page }) => {
  await page.goto("audio/")
  await showsErrorPage(page)
})
