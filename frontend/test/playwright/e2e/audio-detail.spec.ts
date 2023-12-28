import { test, expect, Page } from "@playwright/test"

import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import {
  preparePageForTests,
  turnOnAnalytics,
} from "~~/test/playwright/utils/navigation"

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

test.describe("analytics", () => {
  const audioObject = {
    id: "7e063ee6-343f-48e4-a4a5-f436393730f6",
    provider: "jamendo",
  }
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
    await turnOnAnalytics(page)
  })
  test("sends GET_MEDIA event on CTA button click", async ({
    context,
    page,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToCustomAudioPage(page)

    await page.getByRole("link", { name: /get this audio/i }).click()

    const getMediaEvent = analyticsEvents.find(
      (event) => event.n === "GET_MEDIA"
    )

    expectEventPayloadToMatch(getMediaEvent, {
      ...audioObject,
      mediaType: "audio",
    })
  })

  test("sends AUDIO_INTERACTION event on play", async ({ page, context }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToCustomAudioPage(page)
    await page.getByRole("button", { name: "Play" }).first().click()
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
})

test("shows the 404 error page when no valid id", async ({ page }) => {
  await page.goto("audio/foo")
  await expect(showsErrorPage(page)).resolves.toBeUndefined()
})

test("shows the 404 error page when no id", async ({ page }) => {
  await page.goto("audio/")
  await expect(showsErrorPage(page)).resolves.toBeUndefined()
})
