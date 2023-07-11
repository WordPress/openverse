// Disable no-element-handle for this utility
// It uses them appropriately to do meta-test setup
/* eslint playwright/no-element-handle: ["off"] */

import type { Page } from "@playwright/test"

export const removeHiddenOverflow = async (page: Page) => {
  const mainElement = await page.$(".main.embedded.overflow-x-hidden")
  await mainElement?.evaluate((node) =>
    node.classList.remove("main", "embedded", "overflow-x-hidden")
  )
  mainElement?.dispose()

  const appElement = await page.$(".app.grid.h-screen.overflow-hidden.relative")
  await appElement?.evaluate((node) => node.classList.remove("overflow-hidden"))
  appElement?.dispose()
}

export const hideInputCursors = (page: Page) => {
  return page.addStyleTag({
    content: "* { caret-color: transparent !important; }",
  })
}
