import { test, expect, Page } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

import featureData from "~~/feat/feature-flags.json"

import { getFlagStatus } from "~/stores/feature-flag"
import type { FeatureFlag, FlagName } from "~/types/feature-flag"

const getFeatureCookies = async (page: Page, cookieName: string) => {
  const cookies = await page.context().cookies()
  const cookieValue = cookies.find(
    (cookie) => cookie.name === cookieName
  )?.value
  if (!cookieValue) {
    return {}
  }
  return JSON.parse(decodeURIComponent(cookieValue))
}

/**
 * Ensure that the features to be tested are not out of sync with the feature flags.
 */
const getFeaturesToTest = () => {
  const testableFeatures = {
    fetch_sensitive: "off",
    analytics: "on",
  } as const
  for (const [name, state] of Object.entries(testableFeatures)) {
    const flag = featureData.features[name as FlagName] as FeatureFlag
    if (getFlagStatus(flag) !== "switchable") {
      throw new Error(`Feature ${name} is not switchable`)
    }
    if (flag.defaultState !== state) {
      throw new Error(`Feature ${name} is not in the expected state ${state}`)
    }
  }
  return testableFeatures
}

const features = getFeaturesToTest()

const getSwitchableInput = async (
  page: Page,
  name: string,
  checked: boolean
) => {
  const checkbox = page.locator(`input[type=checkbox]#${name}`).first()
  await expect(checkbox).toBeEnabled()
  if (checked) {
    await expect(checkbox).toBeChecked()
  } else {
    await expect(checkbox).not.toBeChecked()
  }
  return checkbox
}

test.describe("switchable features", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
  })

  for (const [name, defaultState] of Object.entries(features)) {
    const checked = defaultState === "on"

    test(`can switch ${name} from ${defaultState}`, async ({ page }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, checked)
      await featureFlag.click()

      // eslint-disable-next-line playwright/no-conditional-in-test
      if (checked) {
        // eslint-disable-next-line playwright/no-conditional-expect
        await expect(featureFlag).not.toBeChecked()
      } else {
        // eslint-disable-next-line playwright/no-conditional-expect
        await expect(featureFlag).toBeChecked()
      }
    })

    test(`switching ${name} from ${defaultState} saves state in a cookie`, async ({
      page,
    }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, checked)
      await featureFlag.click()

      const storageCookie = { cookie: "features", session: "sessionFeatures" }[
        featureData.features[name as FlagName].storage as "cookie" | "session"
      ]
      const featureCookie = await getFeatureCookies(page, storageCookie)
      expect(featureCookie[name]).toEqual(defaultState === "on" ? "off" : "on")
    })
  }
})
