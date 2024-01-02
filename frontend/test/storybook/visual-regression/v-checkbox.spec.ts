import { test, expect } from "@playwright/test"

test.describe.configure({ mode: "parallel" })

test.describe("VCheckbox", () => {
  test.describe("default", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/iframe.html?id=components-vcheckbox--default-story")
    })

    test("default", async ({ page }) => {
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({ name: "default.png" })
    })

    test("hover", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.hover()
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({ name: "hover.png" })
    })

    test("focused", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.focus()
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({
        name: "focused.png",
      })
    })

    test("disabled", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({
        name: "disabled.png",
      })
    })

    test("on", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.click()
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({ name: "on.png" })
    })

    test("on focused", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.focus()
      await page.keyboard.press("Space")
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({
        name: "on-focused.png",
      })
    })

    test("on disabled", async ({ page }) => {
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.click()
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({
        name: "on-disabled.png",
      })
    })

    test("on-and-off", async ({ page }) => {
      // toggle on and off again
      const checkbox = page.locator('input[type="checkbox"]')
      await checkbox.click()
      // `force: true` is required because the `input`'s pointer events are actually intercepted by the visual SVG.
      // We still want to check that it works though as that does mimic the user behavior of checking directly on the checkbox.
      // eslint-disable-next-line playwright/no-force-option
      await checkbox.click({ force: true })
      expect(
        await page.locator(".screenshot-area").screenshot()
      ).toMatchSnapshot({
        name: "on-and-off.png",
      })
    })
  })
})
