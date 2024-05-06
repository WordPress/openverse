import { expect, Page, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const gotoWithArgs = makeGotoWithArgs(
  "components-vheader-vheadermobile-vfiltertab--default-story"
)

test.describe.configure({ mode: "parallel" })

const wrapper = "[role='tablist']"

const focusFiltersTab = async (page: Page) => {
  await expect(page.locator("#tab-filters")).toBeVisible()
  await page.keyboard.press("Tab")
  const focusedTab = await page.evaluate(
    () => document.activeElement?.textContent ?? ""
  )
  if (focusedTab.includes("Tab1")) {
    await page.keyboard.press("ArrowRight")
  }
}

const hoverFiltersTab = async (page: Page) => {
  await page.locator("#tab-filters").hover()
}

/**
 * Fonts are the last request done by the storybook iframe. This function
 * allows us to wait for the story to be fully-loaded before taking a screenshot.
 */
const goAndWaitForSvg = async (
  page: Page,
  args: Record<string, string | number | boolean>
) => {
  if (args.appliedFilterCount !== 0) {
    await gotoWithArgs(page, args)
  } else {
    const response = page.waitForResponse(/\.svg/)
    await gotoWithArgs(page, args)
    await response
    await expect(page.locator("#tab-filters svg")).toBeVisible()
  }
}

test.describe("VFilterTab", () => {
  for (const appliedFilterCount of [0, 1, 12]) {
    /**
     * If the tab is focused, it will always be selected (it's not manually activated)
     */
    test(`focused, ${appliedFilterCount} filters`, async ({ page }) => {
      await goAndWaitForSvg(page, { appliedFilterCount, isSelected: true })
      await focusFiltersTab(page)

      await expect(page.locator(wrapper)).toHaveScreenshot(
        `filter-tab-focused-${appliedFilterCount}.png`
      )
    })

    test(`focused, hovered, ${appliedFilterCount} filters`, async ({
      page,
    }) => {
      await goAndWaitForSvg(page, { appliedFilterCount })
      await focusFiltersTab(page)
      await hoverFiltersTab(page)

      expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
        `filter-tab-focused-hovered-${appliedFilterCount}.png`
      )
    })

    for (const isSelected of [true, false]) {
      const selected = `${isSelected ? "" : "not_"}selected`
      test(`resting, ${selected}, ${appliedFilterCount} filters`, async ({
        page,
      }) => {
        await goAndWaitForSvg(page, { appliedFilterCount, isSelected })

        expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
          `filter-tab-resting-${selected}-${appliedFilterCount}.png`
        )
      })

      test(`hovered, ${selected}, ${appliedFilterCount} filters`, async ({
        page,
      }) => {
        await goAndWaitForSvg(page, { appliedFilterCount, isSelected })
        await hoverFiltersTab(page)

        expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
          `filter-tab-hovered-${selected}-${appliedFilterCount}.png`
        )
      })
    }
  }
})
