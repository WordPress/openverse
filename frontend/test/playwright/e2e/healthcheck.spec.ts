import { test, expect } from "@playwright/test"

test("returns OK on healthcheck", async ({ page }) => {
  await page.goto("/healthcheck")
  const body = page.locator("body")

  await expect(body).toHaveText("OK")
})
