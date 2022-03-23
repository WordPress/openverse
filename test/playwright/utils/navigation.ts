import { expect, Page } from '@playwright/test'

export const openFilters = async (page: Page) => {
  const filterButtonSelector =
    '[aria-controls="filter-sidebar"], [aria-controls="filter-modal"]'
  const isPressed = async () =>
    await page.getAttribute(filterButtonSelector, 'aria-pressed')
  if ((await isPressed()) !== 'true') {
    await page.click(filterButtonSelector)
    expect(await isPressed()).toEqual('true')
  }
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
  await page.click(`a:has-text("${to}")`)
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
