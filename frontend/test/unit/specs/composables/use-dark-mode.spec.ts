import { describe, expect, test } from "vitest"

import {
  DARK_MODE_CLASS,
  LIGHT_MODE_CLASS,
  useDarkMode,
} from "~/composables/use-dark-mode"
import { OFF, ON } from "~/constants/feature-flag"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"

describe("useDarkMode", () => {
  test.each`
    description                                     | featureFlags                                          | uiColorMode | expectedColorMode | expectedCssClass
    ${"Force dark mode and disable toggling"}       | ${{ force_dark_mode: ON, dark_mode_ui_toggle: OFF }}  | ${"light"}  | ${"dark"}         | ${DARK_MODE_CLASS}
    ${"Don't force dark mode and disable toggling"} | ${{ force_dark_mode: OFF, dark_mode_ui_toggle: OFF }} | ${"dark"}   | ${"light"}        | ${LIGHT_MODE_CLASS}
    ${"Force dark mode and enable toggling"}        | ${{ force_dark_mode: ON, dark_mode_ui_toggle: ON }}   | ${"light"}  | ${"dark"}         | ${DARK_MODE_CLASS}
    ${"Enable toggling, User preference: light"}    | ${{ force_dark_mode: OFF, dark_mode_ui_toggle: ON }}  | ${"light"}  | ${"light"}        | ${LIGHT_MODE_CLASS}
    ${"Enable toggling, User preference: dark"}     | ${{ force_dark_mode: OFF, dark_mode_ui_toggle: ON }}  | ${"dark"}   | ${"dark"}         | ${DARK_MODE_CLASS}
    ${"Enable toggling, User preference: system"}   | ${{ force_dark_mode: OFF, dark_mode_ui_toggle: ON }}  | ${"system"} | ${"system"}       | ${""}
  `(
    "$description: should report colorMode as $expectedColorMode and cssClass as $expectedCssClass",
    ({ featureFlags, uiColorMode, expectedColorMode, expectedCssClass }) => {
      const featureFlagStore = useFeatureFlagStore()

      // Set the feature flags
      featureFlagStore.toggleFeature(
        "force_dark_mode",
        featureFlags.force_dark_mode
      )
      featureFlagStore.toggleFeature(
        "dark_mode_ui_toggle",
        featureFlags.dark_mode_ui_toggle
      )

      // Set the user preference for color mode
      const uiStore = useUiStore()
      uiStore.colorMode = uiColorMode

      // Call the composable
      const { colorMode, cssClass } = useDarkMode()

      // Assert the computed properties
      expect(colorMode.value).toBe(expectedColorMode)
      expect(cssClass.value).toBe(expectedCssClass)
    }
  )
})
