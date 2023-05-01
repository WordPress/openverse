import { expect, Page, test } from "@playwright/test"

import {
  goToSearchTerm,
  renderModes,
  t,
} from "~~/test/playwright/utils/navigation"
import { mockProviderApis } from "~~/test/playwright/utils/route"

import { AUDIO, IMAGE, SupportedMediaType } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const loadMoreButton = `button:has-text("${t("browse-page.load", "ltr")}")`

const openSingleMediaView = async (
  page: Page,
  mediaType: SupportedMediaType
) => {
  const contentLinkSelector =
    mediaType === IMAGE ? "See all images" : "See all audio"
  await page.click(`text=${contentLinkSelector}`)
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
  test.beforeEach(async ({ context }) => {
    await mockProviderApis(context)
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
    await expect(page.locator(loadMoreButton)).toBeVisible()

    await page.click(loadMoreButton)

    expect(additionalRequests.length).toEqual(2)
    expect(additionalRequests.includes(AUDIO)).toBeTruthy()
    expect(additionalRequests.includes(IMAGE)).toBeTruthy()
  })

  for (const mode of renderModes) {
    test.describe(mode, () => {
      test(`Rendered on All view if enough results`, async ({ page }) => {
        await goToSearchTerm(page, "cat", { mode })
        await expect(page.locator(loadMoreButton)).toBeVisible()

        // Load more button is also available on single media type views.
        await openSingleMediaView(page, IMAGE)
        await expect(page.locator(loadMoreButton)).toBeVisible()

        await page.goBack()

        await openSingleMediaView(page, AUDIO)
        await expect(page.locator(loadMoreButton)).toBeVisible()
      })

      test(`Renders on All view when images have results but audio does not`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "ecommerce", { mode })

        await expect(page.locator(loadMoreButton)).toBeVisible()
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
        await goToSearchTerm(page, "horses snort", { mode })

        await page.click(loadMoreButton)
        expect(additionalRequests.length).toEqual(1)
        expect(additionalRequests[0]).toEqual(IMAGE)
      })

      test(`Rendered on All view but not on the audio view when audio has only 1 page of results`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "horses snort", { mode })
        await expect(page.locator(loadMoreButton)).toBeVisible()

        // Cannot go to the audio view because the link is disabled.
        await goToSearchTerm(page, "horses snort", {
          mode,
          searchType: AUDIO,
        })
        await expect(page.locator(loadMoreButton)).not.toBeVisible()
      })
    })
  }
})
