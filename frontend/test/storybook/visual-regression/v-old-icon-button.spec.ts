import { expect, test } from "@playwright/test"

test.describe("VOldIconButton", () => {
  const url = "/iframe.html?id=components-voldiconbutton--sizes"

  test("old icon button sizes", async ({ page }) => {
    await page.goto(url)
    expect(await page.screenshot()).toMatchSnapshot({
      name: "v-old-icon-button-sizes.png",
    })
  })
})
