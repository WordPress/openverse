import { test, expect } from "@playwright/test"

import { goToSearchTerm, setCookies } from "~~/test/playwright/utils/navigation"

test("sends analytics event on external source click", async ({ page }) => {
  let eventData: {
    name: string
    url: string
    mediaType: string
    query: string
  } = { name: "", url: "", mediaType: "", query: "" }
  page.on("request", (req) => {
    if (req.method() === "POST") {
      const requestData = req.postDataJSON()
      if (requestData?.n == "SELECT_EXTERNAL_SOURCE") {
        eventData = JSON.parse(requestData?.p)
      }
    }
  })
  // Start waiting for new page before clicking.
  const pagePromise = page.context().waitForEvent("page")

  const mediaType = "image"
  const name = "Centre For Ageing Better"
  const url =
    "https://ageingbetter.resourcespace.com/pages/search.php?search=cat"
  const query = "cat"

  await setCookies(page.context(), { analytics: "true" })
  await goToSearchTerm(page, "cat", { mode: "SSR", query: "ff_analytics=on" })

  await page.getByRole("button", { name: "Source list" }).click()
  await page.getByRole("link", { name: "Centre for Ageing Better" }).click()

  const newPage = await pagePromise
  await newPage.close()

  expect(eventData.name).toEqual(name)
  expect(eventData.url).toEqual(url)
  expect(eventData.mediaType).toEqual(mediaType)
  expect(eventData.query).toEqual(query)
})
