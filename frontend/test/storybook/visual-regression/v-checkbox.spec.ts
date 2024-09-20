import { test } from "@playwright/test"

import { expectScreenshotAreaSnapshot } from "~~/test/playwright/utils/expect-snapshot"

test.describe.configure({ mode: "parallel" })

test.describe("v-checkbox", () => {
  test.describe("default", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/iframe.html?id=components-vcheckbox--default")
    })

    test("default", async ({ page }) => {
      await expectScreenshotAreaSnapshot(page, "default")
    })

    test("hover", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.hover()

      await expectScreenshotAreaSnapshot(page, "hover")
    })

    test("focused", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.focus()
      await expectScreenshotAreaSnapshot(page, "focused")
    })

    test("disabled", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      await expectScreenshotAreaSnapshot(page, "disabled")
    })

    test("on", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await expectScreenshotAreaSnapshot(page, "on")
    })

    test("on focused", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.focus()
      await page.keyboard.press("Space")
      await expectScreenshotAreaSnapshot(page, "on-focused")
    })

    test("on disabled", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      await expectScreenshotAreaSnapshot(page, "on-disabled")
    })

    test("on-and-off", async ({ page }) => {
      // toggle on and off again
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await checkbox.click()
      await expectScreenshotAreaSnapshot(page, "default")
    })
  })
})
