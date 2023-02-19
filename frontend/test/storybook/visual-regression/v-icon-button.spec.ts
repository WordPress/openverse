import { expect, test } from "@playwright/test"

test.describe("VIconButton", () => {
  const url = "/iframe.html?id=components-viconbutton--sizes"

  test("icon button sizes", async ({ page }) => {
    await page.goto(url)
    expect(await page.screenshot()).toMatchSnapshot({
      name: "v-icon-button-sizes.png",
    })
  })
})
