import { expect, test } from "@playwright/test"

import {
  goToSearchTerm,
  openAndCloseExternalLink,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"

import {
  collectAnalyticsEvents,
  expectEventPayloadToMatch,
} from "~~/test/playwright/utils/analytics"
import { t } from "~~/test/playwright/utils/i18n"

test.describe("analytics", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl", { features: { analytics: "on" } })
  })

  test("sends VIEW_EXTERNAL_SOURCES analytics events", async ({
    page,
    context,
  }) => {
    const events = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat", { searchType: "image", mode: "SSR" })

    await page
      .getByRole("button", { name: t("externalSources.form.supportedTitle") })
      .click()
    await page.getByRole("button", { name: /close/i }).click()

    const viewEvent = events.find(
      (event) => event.n === "VIEW_EXTERNAL_SOURCES"
    )

    expectEventPayloadToMatch(viewEvent, {
      searchType: "image",
      query: "cat",
      resultPage: 1,
    })
  })

  test("sends SELECT_EXTERNAL_SOURCE analytics event and does not send EXTERNAL_LINK_CLICK event", async ({
    page,
    context,
  }) => {
    const events = collectAnalyticsEvents(context)

    await goToSearchTerm(page, "cat", { searchType: "image", mode: "SSR" })

    await page
      .getByRole("button", {
        name: new RegExp(t("externalSources.form.supportedTitleSm"), "i"),
      })
      .click()
    await openAndCloseExternalLink(page, { name: "Centre for Ageing Better" })

    const selectEvent = events.find(
      (event) => event.n === "SELECT_EXTERNAL_SOURCE"
    )

    expectEventPayloadToMatch(selectEvent, {
      name: "Centre For Ageing Better",
      mediaType: "image",
      query: "cat",
      component: "VExternalSourceList",
    })

    const externalLinkClickEvent = events.find(
      (event) => event.n === "EXTERNAL_LINK_CLICK"
    )
    expect(externalLinkClickEvent).toBeUndefined()
  })
})
