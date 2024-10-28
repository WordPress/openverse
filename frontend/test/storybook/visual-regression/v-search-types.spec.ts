import { expect } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

const defaultUrl =
  "/iframe.html?id=components-vcontentswitcher-vsearchtypes--default"

const audioButtonLocator = "text=images"

test.describe.configure({ mode: "parallel" })

test.describe("VSearchTypes", () => {
  breakpoints.describeMd(({ expectSnapshot }) => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${defaultUrl}&args=size%3Amedium`)
      // Ensure the search types have been hydrated
      await expect(page.getByRole("radio").nth(0)).toBeEnabled()
    })
    test("medium resting", async ({ page }) => {
      await expectSnapshot(
        page,
        "v-search-types-medium-at-rest",
        page.locator(".wrapper")
      )
    })

    test("medium images hovered", async ({ page }) => {
      await page.hover(audioButtonLocator)
      await expectSnapshot(
        page,
        "v-search-types-medium-images-hovered",
        page.locator(".wrapper")
      )
    })

    test("medium focused", async ({ page }) => {
      await page.keyboard.press("Tab")
      await expectSnapshot(
        page,
        "v-search-types-medium-focused",
        page.locator(".wrapper")
      )
    })
  })

  breakpoints.describeXl(({ expectSnapshot }) => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${defaultUrl}&args=size%3Asmall`)
      // Ensure the search types have been hydrated
      await expect(page.getByRole("radio").nth(0)).toBeEnabled()
    })

    test("small resting", async ({ page }) => {
      await expectSnapshot(
        page,
        "v-search-types-small-at-rest",
        page.locator(".wrapper")
      )
    })

    test("small images hovered", async ({ page }) => {
      await page.hover(audioButtonLocator)
      await expectSnapshot(
        page,
        "v-search-types-small-images-hovered",
        page.locator(".wrapper")
      )
    })

    test("small focused", async ({ page }) => {
      await page.keyboard.press("Tab")
      await expectSnapshot(
        page,
        "v-search-types-small-focused",
        page.locator(".wrapper")
      )
    })
  })
})
