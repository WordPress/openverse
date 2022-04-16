import { test, expect, Page, BrowserContext } from '@playwright/test'

import { mockProviderApis } from '~~/test/playwright/utils/route'

/**
 * Some helpers for repeated actions.
 */

const reportingEndpoint = '**/report/'

export const visitFirstResult = (page: Page) =>
  page.click('[data-testid="search-results"] a:first-child')
export const openReportModal = (page: Page) =>
  page.click('text="Report this content"')

// Mock a successful reporting response
export const mockReportingEndpoint = (context: BrowserContext) =>
  context.route(reportingEndpoint, (route) => {
    route.fulfill({
      status: 200,
      contentType: 'text/json',
      headers: { 'access-control-allow-origin': '*' },
    })
  })

// Submit the content form and return the network response
export const submitApiReport = (page: Page) =>
  Promise.all([
    page.waitForResponse(reportingEndpoint),
    page.locator('button[type="submit"]:has-text("Report")').click(),
  ]).then((res) => res[0])

/**
 * Reports
 */

const submitDmcaReport = async (page: Page, context: BrowserContext) => {
  // Mock the Google Form to return a successful html document
  await context.route('https://docs.google.com/forms/**', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'text/html',
      body: '<div>Fake form!</div>',
    })
  })
  await page.click('text="Infringes copyright"')
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    await page.click('text="Open form"'), // Opens a new tab
  ])
  await newPage.waitForLoadState()
  return expect(await newPage.url()).toContain('https://docs.google.com/forms')
}

// todo: Test a mature report with the optional description field
const submitMatureContentReport = async (
  page: Page,
  context: BrowserContext
) => {
  await mockReportingEndpoint(context)
  await page.click('text="Contains mature content"')
  const response = await submitApiReport(page)
  return expect(response.status()).toBe(200)
}

const submitOtherReport = async (page: Page, context: BrowserContext) => {
  await mockReportingEndpoint(context)
  await page.click('text="Other"')
  await page.fill(
    'text=Describe the issue',
    'This is an example "Other" report submit by Playwright, our automated e2e test tool.'
  )
  const response = await submitApiReport(page)
  return expect(response.status()).toBe(200)
}

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

const mediaTypes = ['Images', 'Audio']
const reports = {
  dmca: submitDmcaReport,
  mature: submitMatureContentReport,
  other: submitOtherReport,
}

/**
 * Iterate through all the media types and supported reports
 * to make sure every permutation works correctly.
 */
mediaTypes.forEach((mediaType) => {
  Object.entries(reports).forEach(([reportName, reportAssertion]) => {
    test(`Files ${reportName} report for ${mediaType.toLowerCase()}`, async ({
      page,
      context,
    }) => {
      await page.goto('/')
      await page.click(`[aria-label="All content"]`)
      await page.click(`button[role="radio"]:has-text("${mediaType}")`)
      const searchInput = page.locator('main input[type="search"]')
      await searchInput.type('cat')
      await page.click('[aria-label="Search"]')
      await visitFirstResult(page)
      await openReportModal(page)
      await reportAssertion(page, context)
    })
  })
})
