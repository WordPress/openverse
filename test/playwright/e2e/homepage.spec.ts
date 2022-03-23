import { test, expect } from '@playwright/test'

import { mockProviderApis } from '~~/test/playwright/utils/route'

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

test('can change type and search for audio from homepage', async ({ page }) => {
  // Go to http://localhost:8444/
  await page.goto('/')
  await page.click('[aria-label="All content"]')
  await page.click('button[role="radio"]:has-text("Audio")')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')
  const expectedUrl = '/search/audio?q=cat'
  await expect(page).toHaveURL(expectedUrl)
})

test('can search for all results from homepage', async ({ page }) => {
  await page.goto('/')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')

  await expect(page).toHaveURL('search/?q=cat')

  await expect(page.locator('img')).toHaveCount(20)
})
test('can search for images from homepage', async ({ page }) => {
  await page.goto('/')
  await page.click('[aria-label="All content"]')
  await page.click('button[role="radio"]:has-text("Images")')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')

  await expect(page).toHaveURL('search/image?q=cat')

  await expect(page.locator('img')).toHaveCount(20)
})
