const { test, expect } = require('@playwright/test')

test.beforeEach(async ({ context, page }) => {
  // Block any image request for each test in this file.
  await context.route(/\.(png|jpeg|jpg|svg)$/, (route) => route.abort())

  // Test in a custom image detail page, it should apply the same for any image.
  // TODO: Make these tests independent of the live API.
  await page.goto('image/e9d97a98-621b-4ec2-bf70-f47a74380452')
})

test('shows the author and title of the image', async ({ page }) => {
  const author = page.locator('a[aria-label^="author"]')
  await expect(author).toBeVisible()
  const imgTitle = page.locator('h1')
  await expect(imgTitle).toBeVisible()
})

test('shows the main image with its title as alt text', async ({ page }) => {
  const imgTitle = await page.locator('h1').innerText()
  const img = page.locator('img[class="photo_image"]')
  await expect(img).toBeVisible()
  await expect(img).toHaveAttribute('alt', imgTitle)
})

test('does not show back to search results breadcrumb', async ({ page }) => {
  await expect(page.locator('text="Back to search results"')).not.toBeVisible()
})

test('redirects from old /photos/:id route to /image/:id', async ({ page }) => {
  const uuid = 'e9d97a98-621b-4ec2-bf70-f47a74380452'
  await page.goto('photos/' + uuid)
  await expect(page).toHaveURL('image/' + uuid)
})
