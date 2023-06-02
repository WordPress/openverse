// eslint-disable-next-line no-restricted-syntax
import { test as base } from "@playwright/test"

/**
 * This file overwrites the default playwright test fixture
 * to apply some global settings and route handling.
 */
export const test = base.extend({
  page: async ({ page }, use) => {
    // Intercept /api/event requests
    await page.route("/api/event", (route) => route.abort())
    // Intercept  provider APIs
    await page.route("**.jamendo.com**", (route) => route.abort())
    await page.route("**.freesound.**", (route) => route.abort())

    await use(page)
  },
})
