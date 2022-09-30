import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'

const defaultUrl =
  '/iframe.html?id=components-vcontentswitcher-vsearchtypebutton--default-story'
const pressedUrl = `${defaultUrl}&args=pressed:true`

const searchTypeButtonLocator = 'button[aria-haspopup="dialog"]'

test.describe('VSearchTypeButton', () => {
  breakpoints.describeLg(({ expectSnapshot }) => {
    test('resting', async ({ page }) => {
      await page.goto(defaultUrl)
      await expectSnapshot(
        'v-search-type-button-at-rest',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('hovered', async ({ page }) => {
      await page.goto(defaultUrl)
      await page.hover(searchTypeButtonLocator)
      await expectSnapshot(
        'v-search-type-button-hovered',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('pressed', async ({ page }) => {
      await page.goto(pressedUrl)
      await expectSnapshot(
        'v-search-type-button-pressed',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('pressed-hovered', async ({ page }) => {
      await page.goto(pressedUrl)
      await page.hover(searchTypeButtonLocator)
      await expectSnapshot(
        'v-search-type-button-pressed-hovered',
        page.locator(searchTypeButtonLocator)
      )
    })
  })

  breakpoints.describeXl(({ expectSnapshot }) => {
    test('resting', async ({ page }) => {
      await page.goto(defaultUrl)
      await expectSnapshot(
        'v-search-type-button-with-text-at-rest',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('hovered', async ({ page }) => {
      await page.goto(defaultUrl)
      await page.hover(searchTypeButtonLocator)
      await expectSnapshot(
        'v-search-type-button-with-text-hovered',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('pressed', async ({ page }) => {
      await page.goto(pressedUrl)
      await expectSnapshot(
        'v-search-type-button-with-text-pressed',
        page.locator(searchTypeButtonLocator)
      )
    })

    test('pressed-hovered', async ({ page }) => {
      await page.goto(pressedUrl)
      await page.hover(searchTypeButtonLocator)
      await expectSnapshot(
        'v-search-type-button-with-text-pressed-hovered',
        page.locator(searchTypeButtonLocator)
      )
    })
  })
})
