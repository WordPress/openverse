import { test, expect, Page } from "@playwright/test"

import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  preparePageForTests,
  scrollDownAndUp,
} from "~~/test/playwright/utils/navigation"
import { t } from "~~/test/playwright/utils/i18n"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import { getBackToSearchLink } from "~~/test/playwright/utils/components"

const imageObject = {
  id: "e9d97a98-621b-4ec2-bf70-f47a74380452",
  provider: "flickr",
}

const goToCustomImagePage = async (page: Page) => {
  // Test in a custom image detail page, it should apply the same for any image.
  await page.goto(`image/${imageObject.id}`)
  await scrollDownAndUp(page)
}

const errorPageLocator = (page: Page) =>
  page.getByRole("heading", {
    level: 1,
    name: /The content you’re looking for seems to have disappeared/,
  })

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ context, page }) => {
  await mockProviderApis(context)
  await preparePageForTests(page, "xl")
})

test("shows the title of the image", async ({ page }) => {
  await goToCustomImagePage(page)
  const imgTitle = page.locator("h1")
  await expect(imgTitle).toBeVisible()
})

test("shows the main image with its title as alt text", async ({ page }) => {
  await goToCustomImagePage(page)
  const imgTitle = await page.locator("h1").innerText()
  const img = page.locator("id=main-image")
  await expect(img).toBeVisible()
  await expect(img).toHaveAttribute("alt", imgTitle)
})

test("does not show back to search results breadcrumb", async ({ page }) => {
  await goToCustomImagePage(page)
  await expect(getBackToSearchLink(page)).toBeHidden({
    timeout: 300,
  })
})

test("redirects from old /photos/:id route to /image/:id", async ({ page }) => {
  await page.goto(`photos/${imageObject.id}`)
  await expect(page).toHaveURL("image/" + imageObject.id)
})

test("shows the 404 error page when no valid id", async ({ page }) => {
  await page.goto("image/foo")
  await expect(errorPageLocator(page)).toBeVisible()
})

test("shows the 404 error page when no id", async ({ page }) => {
  await page.goto("image/")
  await expect(errorPageLocator(page)).toBeVisible()
})

test("sends GET_MEDIA event on CTA button click", async ({ context, page }) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomImagePage(page)

  await page.getByRole("link", { name: /get this image/i }).click()

  const getMediaEvent = analyticsEvents.find((event) => event.n === "GET_MEDIA")

  expectEventPayloadToMatch(getMediaEvent, {
    id: imageObject.id,
    provider: imageObject.provider,
    mediaType: "image",
  })
})

test("sends RIGHT_CLICK_IMAGE event on right-click", async ({
  context,
  page,
}) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomImagePage(page)

  const img = page.getByRole("img").first()
  await img.click({ button: "right" })

  const rightClickImageEvent = analyticsEvents.find(
    (event) => event.n === "RIGHT_CLICK_IMAGE"
  )

  expectEventPayloadToMatch(rightClickImageEvent, {
    id: imageObject.id,
  })
})

test("sends SELECT_SEARCH_RESULT event on related image click", async ({
  context,
  page,
}) => {
  const analyticsEvents = collectAnalyticsEvents(context)

  await goToCustomImagePage(page)

  await page
    .getByRole("region", { name: t("imageDetails.relatedImages") })
    .locator("img")
    .first()
    .click()
  await page.waitForURL(/image\/1c57f839-6be5-449a-b41a-b1c7de819182/)

  const selectSearchResultEvent = analyticsEvents.find(
    (event) => event.n === "SELECT_SEARCH_RESULT"
  )

  expectEventPayloadToMatch(selectSearchResultEvent, {
    id: "1c57f839-6be5-449a-b41a-b1c7de819182",
    relatedTo: imageObject.id,
    kind: "related",
    mediaType: "image",
    provider: "flickr",
    query: "",
    sensitivities: "",
    isBlurred: false,
    collectionType: null,
    collectionValue: null,
  })
})
