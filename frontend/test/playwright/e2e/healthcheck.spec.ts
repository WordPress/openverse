import { test, expect } from "@playwright/test"

test("returns OK on healthcheck", async ({ page }) => {
  await page.goto("/healthcheck")

  expect(page.textContent("body")).toEqual("OK")
})
