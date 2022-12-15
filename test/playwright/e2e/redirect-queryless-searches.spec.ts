/**
 * Searches without a search term should
 * redirect to the homepage.
 */

import { test, expect } from "@playwright/test"

import { searchTypes, searchPath } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

searchTypes.forEach((type) => {
  test(`Queryless ${type} search redirects to homepage`, async ({ page }) => {
    const response = await page.goto(searchPath(type))
    expect(response?.request().redirectedFrom()?.url()).toBeDefined()
  })
  test(`${type} search with query doesn't redirect`, async ({ page }) => {
    const response = await page.goto(searchPath(type) + "?q=dog")
    expect(response?.request().redirectedFrom()?.url()).toBeUndefined()
  })
})
