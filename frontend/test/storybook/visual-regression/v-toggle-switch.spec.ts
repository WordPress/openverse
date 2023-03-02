import { test, expect } from "@playwright/test"

test.describe.configure({ mode: "parallel" })

test.describe("VToggleSwitch", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/iframe.html?id=components-vtoggleswitch--default-story")
  })

  test("default", async ({ page }) => {
    expect(await page.locator(".screenshot-area").screenshot()).toMatchSnapshot(
      { name: "default.png" }
    )
  })

  test("on", async ({ page }) => {
    const toggleSwitch = page.locator('input[type="checkbox"]')
    await toggleSwitch.click()
    expect(await page.locator(".screenshot-area").screenshot()).toMatchSnapshot(
      { name: "on.png" }
    )
  })

  test("on-and-off", async ({ page }) => {
    // toggle on and off again
    const toggleSwitch = page.locator('input[type="checkbox"]')
    await toggleSwitch.click()

    await toggleSwitch.click()
    expect(await page.locator(".screenshot-area").screenshot()).toMatchSnapshot(
      {
        name: "on-and-off.png",
      }
    )
  })

  test("focused", async ({ page }) => {
    const toggleSwitch = page.locator("#toggle-switch")
    await toggleSwitch.focus()
    expect(await page.locator(".screenshot-area").screenshot()).toMatchSnapshot(
      {
        name: "focused.png",
      }
    )
  })
})
