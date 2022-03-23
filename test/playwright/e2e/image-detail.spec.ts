import { test, expect, Page } from '@playwright/test'

import { mockProviderApis } from '~~/test/playwright/utils/route'

const goToCustomImagePage = async (page: Page) => {
  // Test in a custom image detail page, it should apply the same for any image.
  await page.goto('image/e9d97a98-621b-4ec2-bf70-f47a74380452')
}

const showsErrorPage = async (page: Page) => {
  await expect(page.locator('h1')).toHaveText(
    /The content you’re looking for seems to have disappeared/
  )
}

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

test('shows the author and title of the image', async ({ page }) => {
  await goToCustomImagePage(page)
  const author = page.locator('a[aria-label^="author"]')
  await expect(author).toBeVisible()
  const imgTitle = page.locator('h1')
  await expect(imgTitle).toBeVisible()
})

test('shows the main image with its title as alt text', async ({ page }) => {
  await goToCustomImagePage(page)
  const imgTitle = await page.locator('h1').innerText()
  const img = page.locator('id=main-image')
  await expect(img).toBeVisible()
  await expect(img).toHaveAttribute('alt', imgTitle)
})

test('does not show back to search results breadcrumb', async ({ page }) => {
  await goToCustomImagePage(page)
  await expect(page.locator('text="Back to search results"')).not.toBeVisible({
    timeout: 300,
  })
})

test('redirects from old /photos/:id route to /image/:id', async ({ page }) => {
  const uuid = 'e9d97a98-621b-4ec2-bf70-f47a74380452'
  await page.goto('photos/' + uuid)
  await expect(page).toHaveURL('image/' + uuid)
})

test('shows the 404 error page when no valid id', async ({ page }) => {
  await page.goto('image/foo')
  await showsErrorPage(page)
})

test('shows the 404 error page when no id', async ({ page }) => {
  await page.goto('image/')
  await showsErrorPage(page)
})
