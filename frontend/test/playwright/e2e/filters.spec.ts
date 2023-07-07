import { test, expect, Page } from "@playwright/test"

import {
  changeSearchType,
  goToSearchTerm,
  isPageDesktop,
  filters,
  getCheckbox,
} from "~~/test/playwright/utils/navigation"

import { mockProviderApis } from "~~/test/playwright/utils/route"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import {
  supportedSearchTypes,
  ALL_MEDIA,
  IMAGE,
  AUDIO,
} from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const assertCheckboxCount = async (
  page: Page,
  checked: "checked" | "notChecked" | "total",
  count: number
) => {
  const checkedString = {
    checked: ":checked",
    notChecked: ":not(:checked)",
    total: "",
  }[checked]
  const locatorString = `input[type="checkbox"]${checkedString}`
  await expect(page.locator(locatorString)).toHaveCount(count, { timeout: 200 })
}

const FILTER_COUNTS = {
  [ALL_MEDIA]: 10,
  [AUDIO]: 31,
  [IMAGE]: 69,
}

breakpoints.describeMobileAndDesktop(() => {
  test.beforeEach(async ({ context }) => {
    await mockProviderApis(context)
  })
  for (const searchType of supportedSearchTypes) {
    test(`correct total number of filters is displayed for ${searchType}`, async ({
      page,
    }) => {
      await goToSearchTerm(page, "cat", { searchType })

      await filters.open(page)

      await expect(
        assertCheckboxCount(page, "total", FILTER_COUNTS[searchType])
      ).resolves.toBeUndefined()
    })
  }

  test("initial filters are applied based on the url", async ({ page }) => {
    await page.goto(
      "/search/?q=cat&license_type=commercial&license=cc0&searchBy=creator"
    )
    await filters.open(page)
    // Creator filter was removed from the UI
    const expectedFilters = ["Zero", "Use commercially"]

    for (const checkbox of expectedFilters) {
      await expect(getCheckbox(page, { label: checkbox })).toBeChecked()
    }
  })

  test("common filters are retained when media type changes from all media to single type", async ({
    page,
  }) => {
    await page.goto(
      "/search/?q=cat&license_type=commercial&license=cc0&searchBy=creator"
    )
    await filters.open(page)
    // Creator filter was removed from the UI
    const expectedFilters = ["Zero", "Use commercially"]

    for (const checkbox of expectedFilters) {
      await expect(getCheckbox(page, { label: checkbox })).toBeChecked()
    }
    await changeSearchType(page, IMAGE)

    await expect(page).toHaveURL(
      "/search/image?q=cat&license_type=commercial&license=cc0&searchBy=creator"
    )
    await filters.open(page)
    for (const checkbox of expectedFilters) {
      await expect(getCheckbox(page, { regexp: checkbox })).toBeChecked()
    }
  })

  test("common filters are retained when media type changes from single type to all media", async ({
    page,
  }) => {
    await page.goto(
      "/search/image?q=cat&license_type=commercial&license=cc0&searchBy=creator"
    )
    await filters.open(page)

    // Creator filter was removed from the UI
    for (const checkbox of ["Zero", "Use commercially"]) {
      await expect(getCheckbox(page, { label: checkbox })).toBeChecked()
    }

    await changeSearchType(page, ALL_MEDIA)

    await filters.open(page)
    await expect(page.locator('input[type="checkbox"]:checked')).toHaveCount(2)

    await expect(page).toHaveURL(
      "/search/?q=cat&license_type=commercial&license=cc0&searchBy=creator"
    )
  })

  test("selecting some filters can disable dependent filters", async ({
    page,
  }) => {
    const nonCommercialLicenses = [
      "Attribution-NonCommercial",
      "Attribution-NonCommercial-Share-Alike",
      "Attribution-NonCommercial-NoDerivatives",
    ]
    await page.goto("/search/audio?q=cat&license_type=commercial")
    await filters.open(page)

    await expect(getCheckbox(page, { label: "Use commercially" })).toBeChecked()

    for (const checkbox of nonCommercialLicenses) {
      await expect(getCheckbox(page, { label: checkbox })).not.toBeChecked()
    }

    await page.locator('label:has-text("Use commercially")').click()

    await expect(getCheckbox(page, { label: "Use commercially" })).toBeChecked()

    for (const checkbox of nonCommercialLicenses) {
      await expect(getCheckbox(page, { label: checkbox })).toBeChecked()
    }
  })

  /**
   * When the search type changes:
   * - image-specific filter (aspect_ration=tall) is discarded
   * - common filter (license_type=CC0) is kept
   * - filter button text updates
   * - URL updates
   * Tests for the missing checkbox with `toHaveCount` are flaky, so we use filter button
   * text and the URL instead.
   */
  test("filters are updated when media type changes", async ({ page }) => {
    await page.goto("/search/image?q=cat&aspect_ratio=tall&license=cc0")
    await filters.open(page)

    await expect(getCheckbox(page, { label: "Tall" })).toBeChecked()
    await expect(getCheckbox(page, { label: "Zero" })).toBeChecked()

    await changeSearchType(page, AUDIO)
    await filters.open(page)

    // Only CC0 checkbox is checked, and the filter button label is
    // '1 Filter' on `xl` or '1' on `lg` screens
    await expect(getCheckbox(page, { label: "Zero" })).toBeChecked()

    await filters.close(page)
    // eslint-disable-next-line playwright/no-conditional-in-test
    if (isPageDesktop(page)) {
      const filterButtonText = await page
        .locator('[aria-controls="filters"] span:visible')
        .textContent()
      expect(filterButtonText).toContain("Filters")
    } else {
      const filtersAriaLabel =
        // eslint-disable-next-line playwright/no-conditional-in-test
        (await page
          .locator('[aria-controls="content-settings-modal"]')
          .getAttribute("aria-label")) ?? ""
      expect(filtersAriaLabel.trim()).toEqual("Menu. 1 filter applied")
    }

    await expect(page).toHaveURL("/search/audio?q=cat&license=cc0")
  })

  test("new media request is sent when a filter is selected", async ({
    page,
  }) => {
    await page.goto("/search/image?q=cat")
    await filters.open(page)

    await expect(getCheckbox(page, { label: "Zero" })).toBeChecked()

    // Alternative way with a predicate. Note no await.
    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes("/images/") && response.status() === 200
    )
    await page.getByLabel("Zero").click()
    const response = await responsePromise

    await expect(getCheckbox(page, { label: "Zero" })).toBeChecked()
    // Remove the host url and path because when proxied, the 'http://localhost:49153' is used instead of the
    // real API url
    expect(response.url()).toContain("?q=cat&license=cc0")
  })

  for (const [searchType, source] of [
    ["audio", "Freesound"],
    ["image", "Flickr"],
  ]) {
    test(`Provider filters are correctly initialized from the URL: ${source} - ${searchType}`, async ({
      page,
    }) => {
      await page.goto(
        `/search/${searchType}?q=birds&source=${source.toLowerCase()}`
      )
      await filters.open(page)

      await expect(getCheckbox(page, { label: source })).toBeChecked()
    })
  }
})
