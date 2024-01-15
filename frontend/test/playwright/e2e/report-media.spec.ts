import { test, expect, Page, BrowserContext } from "@playwright/test"

import { mockProviderApis } from "~~/test/playwright/utils/route"
import {
  goToSearchTerm,
  openFirstResult,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

import { supportedMediaTypes } from "~/constants/media"
import { ReportReason } from "~/constants/content-report"

test.describe.configure({ mode: "parallel" })

/**
 * Some helpers for repeated actions.
 */

const reportingEndpoint = "**/report/"

export const openReportModal = (page: Page) =>
  page.click('text="Report this content"')

// Mock a successful reporting response
export const mockReportingEndpoint = (context: BrowserContext) =>
  context.route(reportingEndpoint, (route) =>
    route.fulfill({
      status: 200,
      contentType: "text/json",
      headers: { "access-control-allow-origin": "*" },
    })
  )

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
  await context.route("https://docs.google.com/forms/**", (route) => {
    route.fulfill({
      status: 200,
      contentType: "text/html",
      body: "<div>Fake form!</div>",
    })
  })
  await page.click('text="Infringes copyright"')
  const [newPage] = await Promise.all([
    context.waitForEvent("page"),
    await page.click('text="Open form"'), // Opens a new tab
  ])
  await newPage.waitForLoadState()
  // Return the beginning of the url, without parameters
  return newPage.url().split("/forms/")[0] + "/forms/"
}

// todo: Test a sensitive report with the optional description field
const submitSensitiveContentReport = async (page: Page) => {
  await page.click('text="Contains sensitive content"')
  return (await submitApiReport(page)).status()
}

const submitOtherReport = async (page: Page) => {
  await page.click('text="Other"')
  await page.fill(
    "text=Describe the issue",
    'This is an example "Other" report submit by Playwright, our automated e2e test tool.'
  )
  return (await submitApiReport(page)).status()
}

test.beforeEach(async ({ context, page }) => {
  await mockProviderApis(context)
  await preparePageForTests(page, "xl")
})

const reports = {
  dmca: submitDmcaReport,
  sensitive: submitSensitiveContentReport,
  other: submitOtherReport,
}
const reportResults = {
  dmca: "https://docs.google.com/forms/",
  sensitive: 200,
  other: 200,
}

const mediaObjects = {
  image: {
    id: "f9384235-b72e-4f1e-9b05-e1b116262a29",
    provider: "flickr",
  },
  audio: {
    id: "2ecd5631-c48c-4a5f-89c4-83c44dbbd365",
    provider: "jamendo",
  },
}

/**
 * Iterate through all the media types and supported reports
 * to make sure every permutation works correctly.
 */
supportedMediaTypes.forEach((mediaType) => {
  Object.entries(reports).forEach(([reportName, reportAssertion]) => {
    test(`Files ${reportName} report for ${mediaType}`, async ({
      page,
      context,
    }) => {
      const analyticsEvents = collectAnalyticsEvents(context)
      await mockReportingEndpoint(context)

      await goToSearchTerm(page, "cat", { searchType: mediaType })
      await openFirstResult(page, mediaType)
      await openReportModal(page)
      const result = await reportAssertion(page, context)
      expect(result).toEqual(reportResults[reportName as ReportReason])

      await page
        .getByRole("dialog", { name: /report submitted successfully/ })
        .isVisible()

      const reportMediaEvent = analyticsEvents.find(
        (event) => event.n === "REPORT_MEDIA"
      )

      expectEventPayloadToMatch(reportMediaEvent, {
        ...mediaObjects[mediaType],
        mediaType,
        reason: reportName as ReportReason,
      })
    })
  })
})
