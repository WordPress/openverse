import { expect } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test"

const popoverStory =
  "/iframe.html?id=components-vpopover--control&viewMode=story"

test("VPopover focuses on the first tabbable element in the popover by default", async ({
  page,
}) => {
  await page.goto(popoverStory)
  await page.getByRole("button", { name: "Open" }).click()
  const firstTabbable = page.getByRole("button", { name: "Close popover" })
  await expect(firstTabbable).toBeFocused()
})
