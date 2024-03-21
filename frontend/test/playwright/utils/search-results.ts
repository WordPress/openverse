import { expect, Page } from "@playwright/test"

import { skipToContent } from "~~/test/playwright/utils/navigation"

import { keycodes } from "~/constants/key-codes"
import type { SupportedMediaType } from "~/constants/media"

export const walkToNextOfType = async (type: "image" | "audio", page: Page) => {
  const isActiveElementOfType = () => {
    return page.evaluate(
      ([contextType]) => {
        const regex = new RegExp(`^${contextType}:`, "i")
        const element = document.activeElement as HTMLAnchorElement | null
        const toTest = element?.title || element?.ariaLabel || ""
        return regex.test(toTest)
      },
      [type]
    )
  }

  while (!(await isActiveElementOfType())) {
    await page.keyboard.press(keycodes.Tab)
  }
}

export const walkToType = async (type: "image" | "audio", page: Page) => {
  await skipToContent(page)

  await walkToNextOfType(type, page)
}
export const locateFocusedResult = async (page: Page) => {
  const href = await page.evaluate(
    () => (document.activeElement as HTMLAnchorElement | null)?.href
  )
  expect(href).toBeDefined()
  const url = new URL(href ?? "")

  return page.locator(`[href="${url.pathname}?q=birds"]`)
}

/**
 * Returns the content link from the all content search results page
 * for the given media type.
 */
export const getContentLink = async (
  page: Page,
  mediaType: SupportedMediaType
) => {
  const linkName = new RegExp(`See .+${mediaType}.+found for`)
  return page.getByRole("link", { name: linkName })
}
