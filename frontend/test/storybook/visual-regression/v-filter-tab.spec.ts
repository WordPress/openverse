import { expect, type Page, test } from "@playwright/test"

import { makeUrlWithArgs } from "~~/test/storybook/utils/args"
import { waitForResponse } from "~~/test/storybook/utils/response"

const urlWithArgs = makeUrlWithArgs(
  "components-vheader-vheadermobile-vfiltertab--default"
)

test.describe.configure({ mode: "parallel" })

const wrapper = "[role='tablist']"
const filtersTab = "#tab-filters"

const getFiltersTab = async (page: Page) => page.locator(filtersTab)

const focusFiltersTab = async (page: Page) => {
  const tab = await getFiltersTab(page)
  await expect(tab).toBeVisible()
  await tab.focus()
}

const hoverFiltersTab = async (page: Page) => {
  await (await getFiltersTab(page)).hover()
}

/**
 * Fonts are the last request done by the storybook iframe. This function
 * allows us to wait for the story to be fully-loaded before taking a screenshot.
 */
const goAndWaitForSvg = async (
  page: Page,
  args: Record<string, string | number | boolean>
) => {
  const url = urlWithArgs(args)
  if (args.appliedFilterCount === 0) {
    await waitForResponse(page, url, /\.svg/)
    await expect(page.locator(`${filtersTab} svg`)).toBeVisible()
  } else {
    await page.goto(url)
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

      expect(await page.locator(wrapper).screenshot()).toMatchSnapshot(
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
