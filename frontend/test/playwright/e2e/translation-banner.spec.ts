import { test, expect } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

// Do not use one of the test locales, as those all have "complete" generated translations
const locale = "ru"
const localeSearchPath = `/${locale}/search?q=dog`

test.describe.configure({ mode: "parallel" })

test.describe("translation banner", () => {
  test("Can see the translation banner and go to the correct link", async ({
    page,
  }) => {
    await page.goto(localeSearchPath)
    await expect(page.locator("text= 100")).toBeVisible({ timeout: 500 })

    await page.click("text=contributing a translation")
    await expect(page).toHaveURL(
      `https://translate.wordpress.org/projects/meta/openverse/${locale}/default/`
    )
  })

  test("Banner is not shown if dismissed state is saved in a cookie", async ({
    page,
  }) => {
    await preparePageForTests(page, "xl", { dismissBanners: true })

    await page.goto(localeSearchPath)
    await expect(page.locator('[data-testid="banner-translation"]')).toBeHidden(
      { timeout: 500 }
    )
  })

  test("Can close the translation banner", async ({ page }) => {
    await page.goto(localeSearchPath)
    await page.click('[data-testid="banner-translation"] button:visible')

    const banner = page.locator('.span:has-text("Help us get to 100 percent")')
    await expect(banner).toBeHidden({ timeout: 500 })
    // Test that the banner does not re-appear when navigating to the 'About us' page
    await page.locator(`li a[href="/${locale}/about"]`).click()
    await expect(banner).toBeHidden({ timeout: 500 })

    await page.goto(localeSearchPath)
    await expect(banner).toBeHidden({ timeout: 500 })
  })
})
