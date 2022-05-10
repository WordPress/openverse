import { expect, Page } from '@playwright/test'

const buttonSelectors = {
  filter: '[aria-controls="filters"]',
  contentSwitcher: '[aria-controls="content-switcher-modal"]',
}

const isButtonPressed = async (page: Page, buttonSelector: string) => {
  const viewportSize = page.viewportSize()
  if (!viewportSize) {
    return false
  }
  const pageWidth = viewportSize.width
  if (pageWidth > 640) {
    return await page.getAttribute(buttonSelector, 'aria-pressed')
  } else {
    return (await page.locator('button', { hasText: 'Close' }).isVisible())
      ? 'true'
      : 'false'
  }
}

const openMenu = async (page: Page, button: 'filter' | 'contentSwitcher') => {
  const selector = buttonSelectors[button]
  const expectedValue = 'true'
  if ((await isButtonPressed(page, selector)) !== expectedValue) {
    await page.click(selector)
    expect(await isButtonPressed(page, selector)).toEqual(expectedValue)
  }
}

export const openFilters = async (page: Page) => {
  await openMenu(page, 'filter')
}

export const openMobileMenu = async (page: Page) => {
  await openMenu(page, 'contentSwitcher')
}

export const closeMobileMenu = async (page: Page) => {
  await page.click('text=Close')
}

export const assertCheckboxStatus = async (
  page: Page,
  label: string,
  status: 'checked' | 'unchecked' | 'disabled' = 'checked'
) => {
  const checkbox = page.locator(`label:has-text('${label}')`)
  switch (status) {
    case 'checked': {
      await expect(checkbox).not.toBeDisabled()
      await expect(checkbox).toBeChecked()
      break
    }
    case 'unchecked': {
      await expect(checkbox).not.toBeDisabled()
      await expect(checkbox).not.toBeChecked()
      break
    }
    case 'disabled': {
      await expect(checkbox).toBeDisabled()
    }
  }
}

export const changeContentType = async (
  page: Page,
  to: 'Audio' | 'Images' | 'All content'
) => {
  await page.click(
    `button[aria-controls="content-switcher-popover"], button[aria-controls="content-switcher-modal"]`
  )
  // Ensure that the asynchronous navigation is finished before next steps
  await Promise.all([
    page.waitForNavigation(),
    page.locator(`#content-switcher-popover a:has-text("${to}")`).click(),
  ])
}

/**
 * Finds a button with a popup to the left of the filters button which doesn't have a 'menu' label
 * @param page - The current page
 */
export const currentContentType = async (page: Page) => {
  const contentSwitcherButton = await page.locator(
    `button[aria-controls="content-switcher-popover"], button[aria-controls="content-switcher-modal"]`
  )
  return contentSwitcherButton.textContent()
}

export const dismissTranslationBanner = async (page: Page) => {
  await page
    .locator('[data-testid="banner-translation-ar"] [aria-label="Close"]')
    .click()
}
