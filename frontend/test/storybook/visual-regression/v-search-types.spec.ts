import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

const defaultUrl =
  "/iframe.html?id=components-vcontentswitcher-vsearchtypes--default"

const audioButtonLocator = "text=images"

test.describe.configure({ mode: "parallel" })

test.describe("VSearchTypes", () => {
  breakpoints.describeMd(({ expectSnapshot }) => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${defaultUrl}&args=size%3Amedium`)
    })
    test("medium resting", async ({ page }) => {
      await expectSnapshot("v-search-types-medium-at-rest", page)
    })

    test("medium images hovered", async ({ page }) => {
      await page.hover(audioButtonLocator)
      await expectSnapshot("v-search-types-medium-images-hovered", page)
    })

    test("medium focused", async ({ page }) => {
      await page.keyboard.press("Tab")
      await expectSnapshot("v-search-types-medium-focused", page)
    })
  })

  breakpoints.describeXl(({ expectSnapshot }) => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${defaultUrl}&args=size%3Asmall`)
    })

    test("small resting", async ({ page }) => {
      await expectSnapshot("v-search-types-small-at-rest", page)
    })

    test("small images hovered", async ({ page }) => {
      await page.hover(audioButtonLocator)
      await expectSnapshot("v-search-types-small-images-hovered", page)
    })

    test("small focused", async ({ page }) => {
      await page.keyboard.press("Tab")
      await expectSnapshot("v-search-types-small-focused", page)
    })
  })
})
