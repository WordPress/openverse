import { test, expect, Page } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

const getFeatureCookies = async (page: Page, cookieName: string) => {
  const cookies = await page.context().cookies()
  const cookieValue = cookies.find(
    (cookie) => cookie.name === cookieName
  )?.value
  if (!cookieValue) {
    console.error("no cookie value found for", cookieName, "cookie", cookies)
    return {}
  }
  return JSON.parse(decodeURIComponent(cookieValue))
}

const features = {
  fetch_sensitive: {
    checked: false,
    from: "off",
    to: "on",
    storageCookie: "sessionFeatures",
  },
  additional_search_views: {
    checked: true,
    from: "on",
    to: "off",
    storageCookie: "features",
  },
}

const getSwitchableInput = async (
  page: Page,
  name: string,
  checked: boolean
) => {
  const checkbox = page.locator(`input[type=checkbox]#${name}`).first()
  expect(await checkbox.getAttribute("disabled")).toBeNull()
  if (checked) {
    await expect(checkbox).toHaveAttribute("checked", "checked")
  } else {
    await expect(checkbox).not.toHaveAttribute("checked")
  }
  return checkbox
}

test.describe("switchable features", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
  })

  for (const [name, feature] of Object.entries(features)) {
    test(`can switch ${name} from ${feature.from} to ${feature.to}`, async ({
      page,
    }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, feature.checked)
      await featureFlag.click()

      const inputCheckedStatus = await page
        .locator(`#${name}`)
        .first()
        .getAttribute("checked")
      expect(inputCheckedStatus).toEqual(feature.checked ? "checked" : null)
    })

    test(`switching ${name} from ${feature.from} to ${feature.to} saves state in a cookie`, async ({
      page,
    }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, feature.checked)
      await featureFlag.click()

      const featureCookie = await getFeatureCookies(page, feature.storageCookie)
      expect(featureCookie[name]).toEqual(feature.to)
      expect(1).toEqual(9)
    })
  }
})
