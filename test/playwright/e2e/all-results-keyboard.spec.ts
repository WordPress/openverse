import { test, expect, Page } from '@playwright/test'

import { keycodes } from '~/constants/key-codes'

const walkToType = async (type: 'image' | 'audio', page: Page) => {
  // Go to skip to content button
  await page.keyboard.press(keycodes.Tab)
  // Skip to content
  await page.keyboard.press(keycodes.Enter)

  const isActiveElementOfType = () => {
    return page.evaluate(
      ([contextType]) =>
        new RegExp(
          `/${contextType}/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$`,
          'i'
        ).test(
          (document.activeElement as HTMLAnchorElement | null)?.href ?? ''
        ),
      [type]
    )
  }

  while (!(await isActiveElementOfType())) {
    await page.keyboard.press(keycodes.Tab)
  }
}

const locateFocusedResult = async (page: Page) => {
  const href = await page.evaluate(
    () => (document.activeElement as HTMLAnchorElement | null)?.href
  )
  expect(href).toBeDefined()
  const url = new URL(href ?? '')

  return page.locator(`[href="${url.pathname}"]`)
}

test.describe('all results grid keyboard accessibility test', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search?q=birds')
  })

  test('should open image results as links', async ({ page }) => {
    await walkToType('image', page)
    await page.keyboard.press('Enter')
    await page.waitForURL(
      new RegExp(
        `/image/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$`,
        'i'
      )
    )
  })

  test('should open audio results as links', async ({ page }) => {
    await walkToType('audio', page)
    await page.keyboard.press('Enter')
    await page.waitForURL(
      new RegExp(
        `/audio/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$`,
        'i'
      )
    )
    expect(page.url()).toMatch(
      new RegExp(
        `/audio/[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$`,
        'i'
      )
    )
  })

  test('should allow toggling audio playback via play/pause click', async ({
    page,
  }) => {
    await walkToType('audio', page)
    const focusedResult = await locateFocusedResult(page)
    const playButton = focusedResult.locator('[aria-label="Play"]')
    await playButton.click()

    // should not navigate
    expect(page.url()).toMatch(/\/search\?q=birds$/)

    const pauseButton = focusedResult.locator('[aria-label="Pause"]')
    await expect(pauseButton).toBeVisible()
    await pauseButton.click()
    await expect(playButton).toBeVisible()
  })

  test('should allow toggling audio playback via spacebar', async ({
    page,
  }) => {
    await walkToType('audio', page)
    await page.keyboard.press(keycodes.Spacebar)
    const focusedResult = await locateFocusedResult(page)
    await expect(focusedResult.locator('[aria-label="Pause"]')).toBeVisible()
    await page.keyboard.press(keycodes.Spacebar)
    await expect(focusedResult.locator('[aria-label="Play"]')).toBeVisible()
  })
})
