import { test, expect } from '@playwright/test'

const russianSearchPath = '/ru/search?q=dog'

test.describe.configure({ mode: 'parallel' })

test.describe('translation banner', () => {
  test('Can see the translation banner and go to the correct link', async ({
    page,
  }) => {
    await page.goto(russianSearchPath)
    await expect(
      page.locator(
        'text=The translation for Russian locale is incomplete. Help us get to 100 percent by'
      )
    ).toBeVisible({ timeout: 500 })

    const [page1] = await Promise.all([
      page.waitForEvent('popup'),
      page.click('text=contributing a translation'),
    ])
    await expect(page1).toHaveURL(
      'https://translate.wordpress.org/projects/meta/openverse/ru/default/'
    )
  })

  test('Banner is not shown if dismissed state is saved in a cookie', async ({
    page,
  }) => {
    await page.context().addCookies([
      {
        name: 'uiDismissedBanners',
        value: '["translation-ru"]',
        domain: 'localhost',
        path: '/',
      },
    ])
    await page.goto(russianSearchPath)
    await expect(
      page.locator('[data-testid="banner-translation"]')
    ).not.toBeVisible({ timeout: 500 })
  })

  test('Can close the translation banner', async ({ page }) => {
    await page.goto(russianSearchPath)
    await page.click('[data-testid="banner-translation"] button:visible', {
      timeout: 500,
    })

    const banner = page.locator('.span:has-text("Help us get to 100 percent")')
    await expect(banner).not.toBeVisible({ timeout: 500 })
    // Test that the banner does not re-appear when navigating to the 'About us' page
    await page.click('[aria-label="меню"]')
    await page.click('a[role="menuitemcheckbox"]:has-text("Наша история")')
    await expect(banner).not.toBeVisible({ timeout: 500 })

    await page.goto(russianSearchPath)
    await expect(banner).not.toBeVisible({ timeout: 500 })
  })
})
