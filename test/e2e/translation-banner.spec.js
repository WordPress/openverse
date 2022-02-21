const { test, expect } = require('@playwright/test')

test('Can see the translation banner and go to the correct link', async ({
  page,
}) => {
  await page.goto('/ru/search/')
  await page.click(
    'text=The translation for Russian locale is incomplete. Help us get to 100 percent by '
  )

  const [page1] = await Promise.all([
    page.waitForEvent('popup'),
    page.click('text=contributing a translation'),
  ])
  await expect(page1).toHaveURL(
    'https://translate.wordpress.org/projects/meta/openverse/ru/default/'
  )
})

test('Can close the translation banner', async ({ page }) => {
  await page.goto('/ru/search/')
  await page.click('[aria-label="Закрыть"]')

  const banner = await page.locator(
    '.span:has-text("Help us get to 100 percent")'
  )
  await expect(banner).not.toBeVisible({ timeout: 100 })
  // Test that the banner does not re-appear when navigating to the 'About us' page
  await page.click('[aria-label="меню"]')
  await page.click('a[role="menuitemcheckbox"]:has-text("Наша история")')
  await expect(banner).not.toBeVisible({ timeout: 100 })

  await page.goto('/ru/search/')
  await expect(banner).not.toBeVisible({ timeout: 100 })
})
