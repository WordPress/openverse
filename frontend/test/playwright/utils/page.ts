// Disable no-element-handle for this utility
// It uses them appropriately to do meta-test setup
/* eslint playwright/no-element-handle: ["off"] */

import type { Page } from "@playwright/test"

export const hideInputCursors = (page: Page) => {
  return page.addStyleTag({
    content: "* { caret-color: transparent !important; }",
  })
}
