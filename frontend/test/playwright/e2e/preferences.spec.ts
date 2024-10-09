import { type Page, test } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

import featureData from "~~/feat/feature-flags.json"

import { expectCheckboxState } from "~~/test/playwright/utils/assertions"

import type {
  FeatureFlag,
  FeatureFlagRecord,
  FlagName,
} from "~/types/feature-flag"
import {
  DISABLED,
  FLAG_STATUSES,
  type FlagStatus,
} from "~/constants/feature-flag"
import { DEPLOY_ENVS, type DeployEnv } from "~/constants/deploy-env"

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
  await expectCheckboxState(page, name, checked)
  return page.getByRole("checkbox", { name, checked }).first()
}

const toggleChecked = async (
  page: Page,
  name: string,
  originalChecked: boolean | undefined
) => {
  const featureFlag = await getSwitchableInput(page, name, originalChecked)
  await featureFlag.setChecked(!originalChecked)

  // If the switch knob wasn't rendered yet, wait for it to be rendered.
  // The knob's color is `bg-default` when off and `bg-tertiary` when on.
  await page.evaluate(
    async ([name, className]) => {
      const getKnobClasses = () => {
        return (
          document
            .getElementById(`#${name}`)
            ?.parentElement?.querySelector("span")?.className ?? ""
        )
      }

      for (const waitTime of [100, 200, 500]) {
        if (getKnobClasses().includes(className)) {
          return
        }
        await new Promise((resolve) => setTimeout(resolve, waitTime))
      }
    },
    [name, !originalChecked ? "bg-tertiary" : "bg-default"] as const
  )
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

      await toggleChecked(page, name, checked)

      await expectCheckboxState(page, name, !checked)
    })

    test(`switching ${name} from ${defaultState} saves state in a cookie`, async ({
      page,
    }) => {
      await page.goto(`/preferences`)

      await toggleChecked(page, name, checked)
      await expectCheckboxState(page, name, !checked)

      // Cookies are not visible to the user, so we are checking that the feature flag
      // state is saved and restored when the page is reloaded.
      // If the feature flag is off, the checkbox checked status before user interaction will be undefined,
      // @see https://playwright.dev/docs/api/class-page#page-get-by-role (options.checked section)
      await page.goto(`/preferences`)
      await expectCheckboxState(page, name, checkedAfterToggle)
    })
  }
})
