import { expect, Page } from "@playwright/test"

import { keycodes } from "~/constants/key-codes"

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
  // Go to skip to content button
  await page.keyboard.press(keycodes.Tab)
  // Skip to content
  await page.keyboard.press(keycodes.Enter)

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
