import { expect, Page, test } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

import featureData from "~~/feat/feature-flags.json"

import { expectCheckboxState } from "~~/test/playwright/utils/assertions"

import type {
  FeatureFlag,
  FeatureFlagRecord,
  FlagName,
} from "~/types/feature-flag"
import { DISABLED, FLAG_STATUSES, FlagStatus } from "~/constants/feature-flag"
import { DEPLOY_ENVS, DeployEnv } from "~/constants/deploy-env"

const getFlagStatus = (
  flag: FeatureFlagRecord,
  deployEnv: DeployEnv
): FlagStatus => {
  if (typeof flag.status === "string") {
    if (!FLAG_STATUSES.includes(flag.status as FlagStatus)) {
      console.warn(`Invalid ${flag.description} flag status: ${flag.status}`)
      return DISABLED
    }
    return flag.status as FlagStatus
  } else {
    const envIndex = DEPLOY_ENVS.indexOf(deployEnv)
    for (let i = envIndex; i < DEPLOY_ENVS.length; i += 1) {
      if (DEPLOY_ENVS[i] in flag.status) {
        if (
          !FLAG_STATUSES.includes(flag.status[DEPLOY_ENVS[i]] as FlagStatus)
        ) {
          return DISABLED
        }
        return flag.status[DEPLOY_ENVS[i]] as FlagStatus
      }
    }
  }
  return DISABLED
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
    if (getFlagStatus(flag, "staging") !== "switchable") {
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
  checked: boolean | undefined
) => {
  const checkbox = page.getByRole("checkbox", { name, checked }).first()
  await expect(checkbox).toBeEnabled()
  if (!checked) {
    await expect(checkbox).not.toHaveAttribute("checked")
  }
  return checkbox
}

test.describe("switchable features", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
  })

  for (const [name, defaultState] of Object.entries(features)) {
    const checked = defaultState === "on" || undefined
    const checkedAfterToggle = !checked ? true : undefined

    test(`can switch ${name} from ${defaultState}`, async ({ page }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, checked)
      await featureFlag.click()

      await expectCheckboxState(page, name, !checked)
    })

    test(`switching ${name} from ${defaultState} saves state in a cookie`, async ({
      page,
    }) => {
      await page.goto(`/preferences`)
      const featureFlag = await getSwitchableInput(page, name, checked)

      await featureFlag.click()

      // Ensure the feature flag is updated
      await getSwitchableInput(page, name, !checked)

      await page.goto(`/preferences`)

      // Cookies are not visible to the user, so we are checking that the feature flag
      // state is saved and restored when the page is reloaded.
      // If the feature flag is off, the checkbox checked status before user interaction will be undefined,
      // @see https://playwright.dev/docs/api/class-page#page-get-by-role (options.checked section)
      await expectCheckboxState(page, name, checkedAfterToggle)
    })
  }
})
