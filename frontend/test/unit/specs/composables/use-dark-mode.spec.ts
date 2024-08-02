import { describe, it, expect } from "vitest"

import {
  DARK_MODE_CLASS,
  LIGHT_MODE_CLASS,
  useDarkMode,
} from "~/composables/use-dark-mode"
import { OFF, ON } from "~/constants/feature-flag"
import { useFeatureFlagStore } from "~/stores/feature-flag"

describe("useDarkMode", () => {
  it(`should report isDarkMode as true and cssClass as ${DARK_MODE_CLASS} when the feature flag is enabled`, () => {
    const featureFlagStore = useFeatureFlagStore()
    featureFlagStore.toggleFeature("force_dark_mode", ON)

    // Call the composable
    const { isDarkMode, cssClass } = useDarkMode()

    // Assert the computed properties
    expect(isDarkMode.value).toBe(true)
    expect(cssClass.value).toBe(DARK_MODE_CLASS)
  })

  it(`should report isDarkMode as false and cssClass as ${LIGHT_MODE_CLASS} when the feature flag is disabled`, () => {
    const featureFlagStore = useFeatureFlagStore()
    featureFlagStore.toggleFeature("force_dark_mode", OFF)

    // Call the composable
    const { isDarkMode, cssClass } = useDarkMode()

    // Assert the computed properties
    expect(isDarkMode.value).toBe(false)
    expect(cssClass.value).toBe(LIGHT_MODE_CLASS)
  })
})
