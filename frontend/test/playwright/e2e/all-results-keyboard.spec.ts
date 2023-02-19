import { test, expect, Page } from "@playwright/test"

import audio from "~~/test/playwright/utils/audio"

import { keycodes } from "~/constants/key-codes"

const walkToNextOfType = async (type: "image" | "audio", page: Page) => {
  const isActiveElementOfType = () => {
    return page.evaluate(
      ([contextType]) =>
        new RegExp(
          `/${contextType}/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}\\?q=birds$`,
          "i"
        ).test(
          (document.activeElement as HTMLAnchorElement | null)?.href ?? ""
        ),
      [type]
    )
  }

  while (!(await isActiveElementOfType())) {
    await page.keyboard.press(keycodes.Tab)
  }
}

const walkToType = async (type: "image" | "audio", page: Page) => {
  // Go to skip to content button
  await page.keyboard.press(keycodes.Tab)
  // Skip to content
  await page.keyboard.press(keycodes.Enter)

  await walkToNextOfType(type, page)
}

const locateFocusedResult = async (page: Page) => {
  const href = await page.evaluate(
    () => (document.activeElement as HTMLAnchorElement | null)?.href
  )
  expect(href).toBeDefined()
  const url = new URL(href ?? "")

  return page.locator(`[href="${url.pathname}?q=birds"]`)
}

test.describe.configure({ mode: "parallel" })

test.describe("all results grid keyboard accessibility test", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/search?q=birds")
  })

  test("should open image results as links", async ({ page }) => {
    await walkToType("image", page)
    await page.keyboard.press("Enter")
    await page.waitForURL(
      new RegExp(
        `/image/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}\\?q=birds$`,
        "i"
      )
    )
  })

  test("should open audio results as links", async ({ page }) => {
    await walkToType("audio", page)
    await page.keyboard.press("Enter")
    await page.waitForURL(
      new RegExp(
        `/audio/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}\\?q=birds$`,
        "i"
      )
    )
    expect(page.url()).toMatch(
      new RegExp(
        `/audio/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}\\?q=birds$`,
        "i"
      )
    )
  })

  test("should allow toggling audio playback via play/pause click", async ({
    page,
  }) => {
    await walkToType("audio", page)
    const focusedResult = await locateFocusedResult(page)
    const playButton = await audio.getInactive(focusedResult)
    await playButton.click()
    // should not navigate
    expect(page.url()).toMatch(/\/search\?q=birds$/)

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
    await expect(pauseButton).not.toBeVisible()
  })
})
