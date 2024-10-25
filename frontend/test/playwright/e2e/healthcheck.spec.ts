import { expect } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test"

test("returns OK on healthcheck", async ({ page }) => {
  await page.goto("/healthcheck")
  const body = page.locator("body")

  await expect(body).toHaveText("OK")
})
