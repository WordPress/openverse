const { test, expect } = require('@playwright/test')

test('can change type and search for audio/modification from homepage', async ({
  page,
  context,
}) => {
  // Go to http://localhost:8444/
  await page.goto('/')
  // Click text=Audio
  await page.click('text=Audio')
  // Check text=Modify or adapt >> input[name="lt"]
  await page.check('text=Modify or adapt >> input[name="lt"]')
  // Click [placeholder="Search all content"]
  await page.click('[placeholder="Search all content"]')
  // Fill [placeholder="Search all content"]
  await page.fill('[placeholder="Search all content"]', 'cat')
  // Click button:has-text("Search")
  await page.click('button:has-text("Search")')
  const BASE_URL = context._options.baseURL
  const expectedUrl = BASE_URL + '/search/audio?q=cat&license_type=modification'
  await expect(page).toHaveURL(expectedUrl)
})
