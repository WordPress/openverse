import { test, expect } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"
import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"

test.describe.configure({ mode: "parallel" })

test.describe("attribution", () => {
  test.beforeEach(async ({ context, page }) => {
    await preparePageForTests(page, "xl", { features: { analytics: "on" } })
    await context.grantPermissions(["clipboard-read", "clipboard-write"])
  })

  test("can copy rich text attribution", async ({ page }) => {
    await page.goto("image/e9d97a98-621b-4ec2-bf70-f47a74380452")
    await page.click('[aria-controls="panel-rich"]')
    await page.click('[id="copyattr-rich"]')
    const clippedText = await page.evaluate(async () => {
      return navigator.clipboard.readText()
    })
    // The Clipboard API returns a plain-text-ified version of the rich text.
    expect(clippedText).toContain('"bubbles in honey" by mutednarayan')
  })

  test("can copy HTML attribution", async ({ page }) => {
    await page.goto("image/e9d97a98-621b-4ec2-bf70-f47a74380452")
    await page.click('[aria-controls="panel-html"]')
    await page.click('[id="copyattr-html"]')
    const clippedText = await page.evaluate(async () => {
      return navigator.clipboard.readText()
    })
    const snippets = [
      '<p class="attribution">',
      ">bubbles in honey</a>",
      ">mutednarayan</a>",
    ]
    snippets.forEach((snippet) => {
      expect(clippedText).toContain(snippet)
    })
  })

  test("can copy plain text attribution", async ({ page }) => {
    await page.goto("image/e9d97a98-621b-4ec2-bf70-f47a74380452")
    await page.click('[aria-controls="panel-plain"]')
    await page.click('[id="copyattr-plain"]')
    const clippedText = await page.evaluate(async () => {
      return navigator.clipboard.readText()
    })
    // Only the plain-text license contains the "To view" bit.
    expect(clippedText).toContain("To view a copy of this license")
  })

  test("sends analytics event on copy", async ({ page }) => {
    const analyticsEvents = collectAnalyticsEvents(page.context())

    const mediaType = "image"
    const id = "e9d97a98-621b-4ec2-bf70-f47a74380452"
    const format = "rich"

    await page.goto(`${mediaType}/${id}?ff_analytics=on`)
    await page.click(`[id="copyattr-${format}"]`)

    const copyAttributionEvent = analyticsEvents.find(
      (event) => event.n === "COPY_ATTRIBUTION"
    )
    expectEventPayloadToMatch(copyAttributionEvent, {
      id,
      format,
      mediaType,
    })
  })
})
