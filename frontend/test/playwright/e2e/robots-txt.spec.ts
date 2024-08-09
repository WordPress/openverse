import { test, expect } from "@playwright/test"

test.describe("robots.txt", () => {
  test("snapshot", async ({ page }) => {
    await page.goto("/robots.txt")
    const robotsText = await page.innerText("body")

    expect(robotsText).toMatchSnapshot({ name: "robots.txt" })
  })
})
