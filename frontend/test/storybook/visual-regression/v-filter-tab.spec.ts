import { expect, Page, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const gotoWithArgs = makeGotoWithArgs(
  "components-vheader-vheadermobile-vfiltertab--default-story"
)

test.describe.configure({ mode: "parallel" })

const wrapper = "[role='tablist']"

const focusFiltersTab = async (page: Page) => {
  await page.keyboard.press("Tab")
}

const hoverFiltersTab = async (page: Page) => {
  await page.locator("#tab-filters").hover()
}
test.describe("VFilterTab", () => {
  for (const appliedFilterCount of [0, 1, 12]) {
    /**
     * If the tab is focused, it will always be selected (it's not manually activated)
     */
    test(`focused,${appliedFilterCount} filters`, async ({ page }) => {
      await gotoWithArgs(page, { appliedFilterCount, isSelected: true })
      await focusFiltersTab(page)

      expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
        `filter-tab-focused-${appliedFilterCount}.png`
      )
    })
    test(`focused, hovered, ${appliedFilterCount} filters`, async ({
      page,
    }) => {
      await gotoWithArgs(page, { appliedFilterCount })
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
        await gotoWithArgs(page, { appliedFilterCount, isSelected })
        expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
          `filter-tab-resting-${selected}-${appliedFilterCount}.png`
        )
      })
      test(`hovered, ${selected}, ${appliedFilterCount} filters`, async ({
        page,
      }) => {
        await gotoWithArgs(page, { appliedFilterCount, isSelected })
        await hoverFiltersTab(page)
        expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
          `filter-tab-hovered-${selected}-${appliedFilterCount}.png`
        )
      })
    }
  }
})
