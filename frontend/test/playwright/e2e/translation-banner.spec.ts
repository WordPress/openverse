import { test, expect } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

// Do not use one of the test locales, as those all have "complete" generated translations
const portugueseSearchPath = "/pt/search?q=dog"

test.describe.configure({ mode: "parallel" })

test.describe("translation banner", () => {
  test("Can see the translation banner and go to the correct link", async ({
    page,
  }) => {
    await page.goto(portugueseSearchPath)
    await expect(
      page.locator(
        "text=The translation for Portuguese (Portugal) locale is incomplete. Help us get to 100 percent by"
      )
    ).toBeVisible({ timeout: 500 })

    const [page1] = await Promise.all([
      page.waitForEvent("popup"),
      page.click("text=contributing a translation"),
    ])
    await expect(page1).toHaveURL(
      "https://translate.wordpress.org/projects/meta/openverse/pt/default/"
    )
  })

  test("Banner is not shown if dismissed state is saved in a cookie", async ({
    page,
  }) => {
    await preparePageForTests(page, "xl", { dismissBanners: true })

    await page.goto(portugueseSearchPath)
    await expect(page.locator('[data-testid="banner-translation"]')).toBeHidden(
      { timeout: 500 }
    )
  })

  test("Can close the translation banner", async ({ page }) => {
    await page.goto(portugueseSearchPath)
    await page.click('[data-testid="banner-translation"] button:visible')

    const banner = page.locator('.span:has-text("Help us get to 100 percent")')
    await expect(banner).toBeHidden({ timeout: 500 })
    // Test that the banner does not re-appear when navigating to the 'About us' page
    await page.locator('li a[href="/pt/about"]').click()
    await expect(banner).toBeHidden({ timeout: 500 })

    await page.goto(portugueseSearchPath)
    await expect(banner).toBeHidden({ timeout: 500 })
  })
})
