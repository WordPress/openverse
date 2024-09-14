import { test } from "@playwright/test"

import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

test.describe.configure({ mode: "parallel" })

test.describe("v-checkbox", () => {
  test.describe("default", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/iframe.html?id=components-vcheckbox--default")
    })

    test("default", async ({ page }) => {
      await expectSnapshot("default", page.locator(".screenshot-area"))
    })

    test("hover", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.hover()
      await expectSnapshot("hover", page.locator(".screenshot-area"))
    })

    test("focused", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.focus()
      await expectSnapshot("focused", page.locator(".screenshot-area"))
    })

    test("disabled", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      await expectSnapshot("disabled", page.locator(".screenshot-area"))
    })

    test("on", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await expectSnapshot("on", page.locator(".screenshot-area"))
    })

    test("on focused", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.focus()
      await page.keyboard.press("Space")
      await expectSnapshot("on-focused", page.locator(".screenshot-area"))
    })

    test("on disabled", async ({ page }) => {
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await checkbox.evaluate((checkbox) => {
        ;(checkbox as HTMLInputElement).disabled = true
      })
      await expectSnapshot("on-disabled", page.locator(".screenshot-area"))
    })

    test("on-and-off", async ({ page }) => {
      // toggle on and off again
      const checkbox = page.getByRole("checkbox")
      await checkbox.click()
      await checkbox.click()
      await expectSnapshot("default", page.locator(".screenshot-area"))
    })
  })
})
