import { type Page } from "@playwright/test"

/**
 * Wait for a response to a URL that matches a regex.
 * The pattern of setting up a wait for response without `await`,
 * and awaiting the response after navigating to the URL is used
 * to prevent race conditions.
 * @see https://playwright.dev/docs/api/class-page#page-wait-for-request.
 */
export const waitForResponse = async (
  page: Page,
  url: string,
  responseRegex: RegExp
) => {
  const response = page.waitForResponse(responseRegex)
  await page.goto(url)
  await response
}
