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
    description                                   | featureFlags                    | uiColorMode | expectedColorMode | expectedCssClass
    ${"Disable toggling"}                         | ${{ dark_mode_ui_toggle: OFF }} | ${"dark"}   | ${"light"}        | ${LIGHT_MODE_CLASS}
    ${"Enable toggling, User preference: light"}  | ${{ dark_mode_ui_toggle: ON }}  | ${"light"}  | ${"light"}        | ${LIGHT_MODE_CLASS}
    ${"Enable toggling, User preference: dark"}   | ${{ dark_mode_ui_toggle: ON }}  | ${"dark"}   | ${"dark"}         | ${DARK_MODE_CLASS}
    ${"Enable toggling, User preference: system"} | ${{ dark_mode_ui_toggle: ON }}  | ${"system"} | ${"system"}       | ${""}
  `(
    "$description: should report colorMode as $expectedColorMode and cssClass as $expectedCssClass",
    ({ featureFlags, uiColorMode, expectedColorMode, expectedCssClass }) => {
      const featureFlagStore = useFeatureFlagStore()

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
