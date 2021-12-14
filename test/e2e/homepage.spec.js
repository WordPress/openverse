const { test, expect } = require('@playwright/test')

test('can change type and search for audio/modification from homepage', async ({
  page,
  baseURL,
}) => {
  // Go to http://localhost:8444/
  await page.goto('/')
  await page.click('text=Audio')
  await page.check('text=Modify or adapt >> input[name="licenseType"]')
  await page.click('[placeholder="Search all content"]')
  await page.fill('[placeholder="Search all content"]', 'cat')
  await page.click('button:has-text("Search")')
  const expectedUrl = baseURL + '/search/audio?q=cat&license_type=modification'
  await expect(page).toHaveURL(expectedUrl)
})

test('can search for images from homepage, and then load more results', async ({
  page,
  baseURL,
}) => {
  // Go to http://localhost:8444/
  await page.goto('/')
  await page.click('[placeholder="Search all content"]')
  await page.fill('[placeholder="Search all content"]', 'cat')
  await page.click('button:has-text("Search")')
  const expectedUrl = baseURL + '/search/image?q=cat'
  await expect(page).toHaveURL(expectedUrl)

  await expect(page.locator('img')).toHaveCount(20)
  await page.click('button:has-text("Load more")')
  await expect(page.locator('img')).toHaveCount(40)
})
