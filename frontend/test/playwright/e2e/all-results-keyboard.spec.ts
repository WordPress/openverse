import { expect, test } from "@playwright/test"

import audio from "~~/test/playwright/utils/audio"
import {
  goToSearchTerm,
  preparePageForTests,
  skipToContent,
} from "~~/test/playwright/utils/navigation"

import {
  getContentLink,
  locateFocusedResult,
  walkToNextOfType,
  walkToType,
} from "~~/test/playwright/utils/search-results"

import { keycodes } from "~/constants/key-codes"
import { SupportedMediaType } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const singleResultRegex = (
  mediaType: SupportedMediaType,
  searchTerm?: string
) => {
  const query = searchTerm ? `\\?q=${searchTerm}` : ""
  return new RegExp(
    `/${mediaType}/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}${query}$`,
    "i"
  )
}

test.describe("all results grid keyboard accessibility test", () => {
  const searchTerm = "birds"
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
    await goToSearchTerm(page, searchTerm)
  })

  test("should open image results as links", async ({ page }) => {
    const mediaType = "image"
    await walkToType(mediaType, page)
    await page.keyboard.press("Enter")
    const urlRegex = singleResultRegex(mediaType, searchTerm)

    await page.waitForURL(urlRegex)
    expect(page.url()).toMatch(urlRegex)
  })

  test("should open audio results as links", async ({ page }) => {
    const mediaType = "audio"
    await walkToType(mediaType, page)
    await page.keyboard.press("Enter")
    const urlRegex = singleResultRegex(mediaType, searchTerm)
    await page.waitForURL(urlRegex)
    expect(page.url()).toMatch(urlRegex)
  })

  test("should show instructions snackbar when focusing first audio", async ({
    page,
  }) => {
    await walkToType("audio", page)

    await expect(page.locator("[role=alert]")).toBeVisible()
  })

  test("should hide the instructions snackbar when interacted with audio", async ({
    page,
  }) => {
    await walkToType("audio", page)

    await expect(page.locator("[role=alert]")).toBeVisible()

    const focusedResult = await locateFocusedResult(page)
    const playButton = await audio.getInactive(focusedResult)
    await playButton.click()

    await expect(page.locator("[role=alert]")).toBeHidden()
  })

  test("should allow toggling audio playback via play/pause click", async ({
    page,
  }) => {
    await walkToType("audio", page)
    const focusedResult = await locateFocusedResult(page)
    const playButton = await audio.getInactive(focusedResult)
    await playButton.click()

    // Get the path for comparison purposes
    const url = new URL(page.url())
    const path = url.pathname + url.search

    // should not navigate
    expect(path).toMatch(/\/search\/?\?q=birds$/)

    const pauseButton = await audio.getActive(focusedResult)
    pauseButton.click()
    await expect(playButton).toBeVisible()
  })

  test("should allow toggling audio playback via spacebar", async ({
    page,
  }) => {
    await walkToType("audio", page)
    await page.keyboard.press(keycodes.Spacebar)
    const focusedResult = await locateFocusedResult(page)
    await expect(await audio.getActive(focusedResult)).toBeVisible()
    await page.keyboard.press(keycodes.Spacebar)
    await expect(await audio.getInactive(focusedResult)).toBeVisible()
  })

  test("should pause audio after playing another", async ({ page }) => {
    await walkToType("audio", page)
    const focusedResult = await locateFocusedResult(page)
    const playButton = await audio.getInactive(focusedResult)
    await playButton.click()
    const pauseButton = await audio.getActive(focusedResult)

    await page.keyboard.press(keycodes.Tab)
    await walkToNextOfType("audio", page)

    const nextFocusedResult = await locateFocusedResult(page)
    const nextPlayButton = await audio.getInactive(nextFocusedResult)
    await nextPlayButton.click()
    await audio.getActive(nextFocusedResult)

    await expect(playButton).toBeVisible()
    await expect(pauseButton).toBeHidden()
  })

  // Test for https://github.com/WordPress/openverse/issues/3940
  test("clicking on skip-to-content should not navigate", async ({ page }) => {
    const getResultsLabel = async (type: SupportedMediaType) => {
      const link = await getContentLink(page, type)
      return link.textContent()
    }
    const imageResultsLabel = await getResultsLabel("image")
    const audioResultsLabel = await getResultsLabel("audio")

    await skipToContent(page)

    expect(await getResultsLabel("image")).toEqual(imageResultsLabel)
    expect(await getResultsLabel("audio")).toEqual(audioResultsLabel)
  })
})
