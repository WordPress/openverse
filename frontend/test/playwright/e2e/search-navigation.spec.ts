import { expect, Page, test } from "@playwright/test"

import {
  goToSearchTerm,
  filters,
  searchFromHeader,
  openFirstResult,
  t,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { mockProviderApis } from "~~/test/playwright/utils/route"
import breakpoints from "~~/test/playwright/utils/breakpoints"

import { AUDIO, IMAGE, SupportedMediaType } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const getContentLink = async (page: Page, mediaType: SupportedMediaType) => {
  const linkName = new RegExp(`See .+${mediaType}.+found for`)
  return page.getByRole("link", { name: linkName })
}

test.describe("search history navigation", () => {
  breakpoints.describeMobileAndDesktop(({ breakpoint }) => {
    test.beforeEach(async ({ context, page }) => {
      await mockProviderApis(context)
      await preparePageForTests(page, breakpoint)
    })

    test("should update search results when back navigation changes filters", async ({
      page,
    }) => {
      await goToSearchTerm(page, "galah")
      // Open filter sidebar
      await filters.open(page)

      const modifyLocator = page.getByRole("checkbox", {
        name: "Modify or adapt",
      })
      // Apply a filter
      await modifyLocator.click()
      // There is a debounce when choosing a filter.
      // we need to wait for the page to reload before running the test
      await page.waitForURL(/license_type=modification/)

      // Verify the filter is applied to the URL and the checkbox is checked
      // Note: Need to add that a search was actually executed with the new
      // filters and that the page results have been updated for the new filters
      // @todo(sarayourfriend): ^?
      await expect(modifyLocator).toBeChecked()

      // Navigate backwards and verify URL is updated and the filter is unapplied
      await page.goBack()

      // Ditto here about the note above, need to verify a new search actually happened with new results
      expect(page.url()).not.toContain("license_type=modification")
      await expect(modifyLocator).not.toBeChecked()
    })

    test("should update search results when back button updates search type", async ({
      page,
    }) => {
      await goToSearchTerm(page, "galah")
      await page
        .getByRole("link", { name: /See.*images found for .*/i })
        .click()

      // There are no content links on single media type search pages
      await expect(await getContentLink(page, IMAGE)).toBeHidden()
      expect(page.url()).toContain("/search/image")

      await page.goBack({ waitUntil: "networkidle" })

      await expect(await getContentLink(page, IMAGE)).toBeVisible()
      await expect(await getContentLink(page, AUDIO)).toBeVisible()
    })

    test("should update search term when back button is clicked", async ({
      page,
    }) => {
      await goToSearchTerm(page, "galah")

      await searchFromHeader(page, "cat")
      await expect(page.locator('input[name="q"]')).toHaveValue("cat")

      await page.goBack()

      await expect(await getContentLink(page, IMAGE)).toBeVisible()
      await expect(page.locator('input[name="q"]')).toHaveValue("galah")
    })

    test("navigates to the image detail page correctly", async ({ page }) => {
      await goToSearchTerm(page, "honey")
      const figure = page.locator("figure").first()
      const imgTitle = await figure.locator("img").getAttribute("alt")

      await page.locator('a[href^="/image"]').first().click()
      // Until the image is loaded, the heading is 'Image' instead of the actual title
      await page.locator("#main-image").waitFor()

      const headingText = await page.locator("h1").textContent()
      expect(headingText?.trim().toLowerCase()).toEqual(imgTitle?.toLowerCase())
    })

    test.describe("back to search results link", () => {
      test("is visible in breadcrumb when navigating to image details page and returns to the search page", async ({
        page,
      }) => {
        const url = "/search?q=galah"
        await page.goto(url)
        await page.locator('a[href^="/image"]').first().click()
        const link = page.locator(`text="${t("singleResult.back")}"`)
        await expect(link).toBeVisible()
        await link.click()
        await expect(page).toHaveURL(url)
      })

      test("is visible in breadcrumb when navigating to localized image details page", async ({
        page,
      }) => {
        await page.goto("/es/search/?q=galah")
        await page.locator('a[href^="/es/image"]').first().click()
        await expect(
          page.locator('text="Volver a los resultados de búsqueda"')
        ).toBeVisible()
      })

      test("is visible in breadcrumb when navigating to localized audio details page", async ({
        page,
      }) => {
        await page.goto("/es/search/?q=galah")
        await page.locator('a[href^="/es/audio"]').first().click()
        await expect(
          page.locator('text="Volver a los resultados de búsqueda"')
        ).toBeVisible()
      })
    })
  })
})

test.describe("search query param is set on a single page results", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`/search?q=cat`)
  })

  test("the search query param should be set to the search term inside the header on a single page result of type image", async ({
    page,
  }) => {
    await openFirstResult(page, "image")
    const url = page.url()
    const query = url.substring(url.indexOf("=") + 1)

    expect(query).toEqual("cat")
  })

  test("the search query param should be set to the search term inside the header on a single page result of type audio", async ({
    page,
  }) => {
    await openFirstResult(page, "audio")
    const url = page.url()
    const query = url.substring(url.indexOf("=") + 1)

    expect(query).toEqual("cat")
  })
})
