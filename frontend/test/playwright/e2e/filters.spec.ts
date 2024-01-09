import { test, expect, Page } from "@playwright/test"

import {
  changeSearchType,
  goToSearchTerm,
  isPageDesktop,
  filters,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"

import { mockProviderApis } from "~~/test/playwright/utils/route"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import enMessages from "~/locales/en.json"

import {
  supportedSearchTypes,
  ALL_MEDIA,
  IMAGE,
  AUDIO,
  SupportedMediaType,
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

// Note that this includes two switches for sensitive content preferences.
const FILTER_COUNTS = {
  [ALL_MEDIA]: 12,
  [AUDIO]: 33,
  [IMAGE]: 73,
}

breakpoints.describeMobileAndDesktop(({ breakpoint }) => {
  test.beforeEach(async ({ context, page }) => {
    await mockProviderApis(context)
    await preparePageForTests(page, breakpoint, { dismissFilter: false })
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
    await page.goto("/search?q=cat&license_type=commercial&license=cc0")
    await filters.open(page)
    // Creator filter was removed from the UI
    const expectedFilters = ["Zero", "Use commercially"]

    for (const checkbox of expectedFilters) {
      await expect(page.getByRole("checkbox", { name: checkbox })).toBeChecked()
    }
  })

  test("common filters are retained when media type changes from all media to single type", async ({
    page,
  }) => {
    await page.goto("/search?q=cat&license_type=commercial&license=cc0")
    await filters.open(page)
    // Creator filter was removed from the UI
    const expectedFilters = ["Zero", "Use commercially"]

    for (const checkbox of expectedFilters) {
      await expect(page.getByRole("checkbox", { name: checkbox })).toBeChecked()
    }
    await changeSearchType(page, IMAGE)

    await expect(page).toHaveURL(
      "/search/image?q=cat&license_type=commercial&license=cc0"
    )
    await filters.open(page)
    for (const checkbox of expectedFilters) {
      await expect(page.getByRole("checkbox", { name: checkbox })).toBeChecked()
    }
  })

  test("common filters are retained when media type changes from single type to all media", async ({
    page,
  }) => {
    await page.goto("/search/image?q=cat&license_type=commercial&license=cc0")
    await filters.open(page)

    // Creator filter was removed from the UI
    for (const checkbox of ["Zero", "Use commercially"]) {
      await expect(page.getByRole("checkbox", { name: checkbox })).toBeChecked()
    }

    await changeSearchType(page, ALL_MEDIA)

    await filters.open(page)
    await expect(page.locator('input[type="checkbox"]:checked')).toHaveCount(3)

    await expect(page).toHaveURL(
      "/search?q=cat&license_type=commercial&license=cc0"
    )
  })

  test("selecting some filters can disable dependent filters", async ({
    page,
  }) => {
    // Ignore the "+" licenses which are not presented on the page
    // `exact: true` is required in locators later in this test to prevent "Attribution" from matching
    // all CC licenses with the BY element (all of them :P)
    const allLicenses = Object.values(enMessages.licenseReadableNames).filter(
      (l) => !l.includes("Plus")
    )
    const nonCommercialLicenses = allLicenses.filter((l) =>
      l.includes("NonCommercial")
    )
    const commercialLicenses = allLicenses.filter(
      (l) => !nonCommercialLicenses.includes(l)
    )

    await page.goto("/search/audio?q=cat")
    await filters.open(page)

    await expect(
      page.getByRole("checkbox", { name: "Use commercially" })
    ).not.toBeChecked()

    // Use commercially is not enabled yet, so commercial licenses are still available
    // Therefore, all active licenses should have enabled checkboxes
    for (const checkbox of allLicenses) {
      const element = page.getByRole("checkbox", {
        name: checkbox,
        exact: true,
      })
      await expect(element).toBeVisible()
      await expect(element).toBeEnabled()
    }

    // Enable the commercial use filter
    await page.locator('label:has-text("Use commercially")').click()
    await page.waitForURL(/license_type=commercial/)

    await expect(
      page.getByRole("checkbox", { name: "Use commercially" })
    ).toBeChecked()

    // Because we checked "Use commercially", licenses that disallow commercial
    // use will be disabled and the rest will still be enabled.
    // Additionally, none of the checkboxes will be checked because we've only
    // manipulated the commercial filter, not any specific license filters
    for (const checkbox of nonCommercialLicenses) {
      await expect(
        page.getByRole("checkbox", { name: checkbox, exact: true })
      ).not.toBeChecked()
      await expect(
        page.getByRole("checkbox", { name: checkbox, exact: true })
      ).toBeDisabled()
    }

    for (const checkbox of commercialLicenses) {
      await expect(
        page.getByRole("checkbox", { name: checkbox, exact: true })
      ).not.toBeChecked()
      await expect(
        page.getByRole("checkbox", { name: checkbox, exact: true })
      ).toBeEnabled()
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

    await expect(page.getByRole("checkbox", { name: "Tall" })).toBeChecked()
    await expect(page.getByRole("checkbox", { name: "Zero" })).toBeChecked()

    await changeSearchType(page, AUDIO)
    await filters.open(page)

    // Only CC0 checkbox is checked, and the filter button label is
    // '1 Filter' on `xl` or '1' on `lg` screens
    await expect(page.getByRole("checkbox", { name: "Zero" })).toBeChecked()

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

    await expect(page.getByRole("checkbox", { name: "Zero" })).not.toBeChecked()

    // Alternative way with a predicate. Note no await.
    const responsePromise = page.waitForResponse(
      (response) =>
        response.url().includes("/images/") && response.status() === 200
    )
    await page.getByLabel("Zero").click()
    const response = await responsePromise

    await expect(page.getByRole("checkbox", { name: "Zero" })).toBeChecked()
    // Remove the host url and path because when proxied, the 'http://localhost:49153' is used instead of the
    // real API url
    expect(response.url()).toContain("?q=cat&license=cc0")
  })

  for (const [searchType, source] of [
    ["audio", "Freesound"],
    ["image", "Flickr"],
  ] as [SupportedMediaType, string][]) {
    test(`Provider filters are correctly initialized from the URL: ${source} - ${searchType}`, async ({
      page,
    }) => {
      await goToSearchTerm(page, "birds", {
        searchType,
        query: `source=${source.toLowerCase()}`,
      })
      await filters.open(page)

      await expect(page.getByRole("checkbox", { name: source })).toBeChecked()
    })
  }

  test("sends APPLY_FILTER event", async ({ context, page }) => {
    const events = collectAnalyticsEvents(context)
    await goToSearchTerm(page, "cat")

    await filters.open(page)
    await page.getByRole("checkbox", { name: /use commercially/i }).click()

    const applyFilterEvent = events.find((e) => e.n === "APPLY_FILTER")

    expectEventPayloadToMatch(applyFilterEvent, {
      category: "licenseTypes",
      key: "commercial",
      checked: true,
      query: "cat",
      searchType: ALL_MEDIA,
    })
  })
})

breakpoints.describeLg(({ breakpoint }) => {
  test("sends TOGGLE_FILTER_SIDEBAR event", async ({ context, page }) => {
    const events = collectAnalyticsEvents(context)
    await preparePageForTests(page, breakpoint, { dismissFilter: false })
    await goToSearchTerm(page, "cat")

    await filters.close(page)
    await expect(page.locator("#filters")).toBeHidden()

    await filters.open(page)
    await expect(page.locator("#filters")).toBeVisible()

    const toggleFilterSidebarEvents = events.filter(
      (e) => e.n === "TOGGLE_FILTER_SIDEBAR"
    )

    expectEventPayloadToMatch(toggleFilterSidebarEvents[0], {
      searchType: ALL_MEDIA,
      toState: "closed",
    })
    expectEventPayloadToMatch(toggleFilterSidebarEvents[1], {
      searchType: ALL_MEDIA,
      toState: "opened",
    })
  })
})
