import { expect, Page, test } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
  renderModes,
} from "~~/test/playwright/utils/navigation"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import { getLoadMoreButton } from "~~/test/playwright/utils/components"

import { AUDIO, IMAGE, SupportedMediaType } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const openSingleMediaView = async (
  page: Page,
  mediaType: SupportedMediaType
) => {
  await page
    .getByRole("link", { name: new RegExp(`See .+ ${mediaType}.+found for`) })
    .click()
  await page.waitForURL(/search\/(audio|image)/)
}
/**
 * Cases, check both SSR and CSR:
 * 1. All content view with more than 1 page of results for each media type:
 *  - should have a Load more button.
 *  - each individual media type view should have a Load more button.
 *  - when button is clicked, should fetch all media types.
 * 2. All content view with results for images, but only 1 page of results for audio:
 *  - should have a Load more button.
 *  - when button is clicked, should fetch only images.
 *  - image view should have a Load more button, but audio view should not.
 * 3. All content view with results for images, but no results for audio:
 *  - should have a Load more button.
 *  - when button is clicked, should fetch only images.
 *  - image view should have a Load more button.
 */

test.describe("Load more button", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
  })

  test("Clicking sends 2 requests on All view with enough results", async ({
    page,
  }) => {
    const additionalRequests = [] as SupportedMediaType[]
    page.on("request", (re) => {
      const url = re.url()
      if (url.includes("page=2")) {
        if (url.includes("/audio/")) {
          additionalRequests.push(AUDIO)
        } else if (url.includes("/images/")) {
          additionalRequests.push(IMAGE)
        }
      }
    })
    await goToSearchTerm(page, "cat")

    await getLoadMoreButton(page).click()

    expect(additionalRequests.length).toEqual(2)
    expect(additionalRequests.includes(AUDIO)).toBeTruthy()
    expect(additionalRequests.includes(IMAGE)).toBeTruthy()
  })

  for (const mode of renderModes) {
    test.describe(mode, () => {
      test(`Rendered on All view if enough results`, async ({ page }) => {
        await goToSearchTerm(page, "cat", { mode })

        const loadMoreButton = getLoadMoreButton(page)
        await expect(loadMoreButton).toBeVisible()

        // Load more button is also available on single media type views.
        await openSingleMediaView(page, IMAGE)
        await expect(loadMoreButton).toBeVisible()

        await page.goBack()

        await openSingleMediaView(page, AUDIO)
        await expect(loadMoreButton).toBeVisible()
      })

      test(`Renders on All view when images have results but audio does not`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "ecommerce", { mode })

        await expect(getLoadMoreButton(page)).toBeVisible()
      })

      test(`All view when only 1 page of audio: sends only image request when clicked`, async ({
        page,
      }) => {
        const additionalRequests = [] as SupportedMediaType[]
        page.on("request", (req) => {
          const url = req.url()
          if (url.includes("page=2")) {
            if (url.includes("/audio/")) {
              additionalRequests.push(AUDIO)
            } else if (url.includes("/images/")) {
              additionalRequests.push(IMAGE)
            }
          }
        })
        await goToSearchTerm(page, "horses snort window", { mode })

        await getLoadMoreButton(page).click()
        expect(additionalRequests.length).toEqual(1)
      })

      test(`Rendered on All view but not on the audio view when audio has only 1 page of results`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "horses snort window", { mode })

        await expect(getLoadMoreButton(page)).toBeVisible()

        // Cannot go to the audio view because the link is disabled.
        await goToSearchTerm(page, "horses snort window", {
          mode,
          searchType: AUDIO,
        })
        await expect(getLoadMoreButton(page)).toBeHidden()
      })
    })
  }

  /**
   * Checks that an analytics event is posted to /api/event and has the correct
   * payload for the REACH_RESULT_END event.
   */
  test(`Sends a valid REACH_RESULT_END event when user reaches the load more page`, async ({
    page,
    context,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat")
    const loadMoreButton = getLoadMoreButton(page)

    await loadMoreButton.scrollIntoViewIfNeeded()
    await expect(loadMoreButton).toBeVisible()

    const reachResultEndEvent = analyticsEvents.find(
      (event) => event.n === "REACH_RESULT_END"
    )

    expectEventPayloadToMatch(reachResultEndEvent, {
      query: "cat",
      searchType: "all",
      resultPage: 1,
      collectionType: null,
      collectionValue: null,
    })
  })

  test(`is sent when loading one page of results.`, async ({
    page,
    context,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat")
    await getLoadMoreButton(page).click()

    const loadMoreEvent = analyticsEvents.find(
      (event) => event.n === "LOAD_MORE_RESULTS"
    )

    expectEventPayloadToMatch(loadMoreEvent, {
      query: "cat",
      searchType: "all",
      resultPage: 1,
      collectionType: null,
      collectionValue: null,
    })
  })

  test(`is sent when loading two pages of results.`, async ({
    page,
    context,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat")
    const loadMoreButton = getLoadMoreButton(page)

    await loadMoreButton.click()
    await loadMoreButton.click()

    const loadMoreEvents = analyticsEvents.filter(
      (event) => event.n === "LOAD_MORE_RESULTS"
    )

    expect(loadMoreEvents.length).toBe(2)
    loadMoreEvents.every((event, index) =>
      expectEventPayloadToMatch(event, {
        query: "cat",
        searchType: "all",
        resultPage: index + 1,
        collectionType: null,
        collectionValue: null,
      })
    )
  })

  test(`is not sent when more results are not loaded.`, async ({
    page,
    context,
  }) => {
    const analyticsEvents = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat")
    await expect(getLoadMoreButton(page)).toBeVisible()

    const loadMoreEvents = analyticsEvents.filter(
      (event) => event.n === "LOAD_MORE_RESULTS"
    )

    expect(loadMoreEvents.length).toBe(0)
  })
})
