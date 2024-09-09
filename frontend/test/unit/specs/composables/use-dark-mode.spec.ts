import { computed } from "#imports"

import { describe, expect, test, vi } from "vitest"

import { usePreferredColorScheme } from "@vueuse/core"

import {
  DARK_MODE_CLASS,
  LIGHT_MODE_CLASS,
  useDarkMode,
} from "~/composables/use-dark-mode"
import { OFF, ON } from "~/constants/feature-flag"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"

vi.mock("@vueuse/core", () => ({
  usePreferredColorScheme: vi.fn(),
}))

describe("useDarkMode", () => {
  test.each`
    description                                                | featureFlags                    | uiColorMode | osColorMode        | expectedColorMode | expectedEffectiveColorMode | expectedCssClass
    ${"Toggle: off"}                                           | ${{ dark_mode_ui_toggle: OFF }} | ${"dark"}   | ${"dark"}          | ${"light"}        | ${"light"}                 | ${LIGHT_MODE_CLASS}
    ${"Toggle: on, Preference: light"}                         | ${{ dark_mode_ui_toggle: ON }}  | ${"light"}  | ${"dark"}          | ${"light"}        | ${"light"}                 | ${LIGHT_MODE_CLASS}
    ${"Toggle: on, Preference: dark"}                          | ${{ dark_mode_ui_toggle: ON }}  | ${"dark"}   | ${"light"}         | ${"dark"}         | ${"dark"}                  | ${DARK_MODE_CLASS}
    ${"Toggle: on, Preference: system, System: light"}         | ${{ dark_mode_ui_toggle: ON }}  | ${"system"} | ${"light"}         | ${"system"}       | ${"light"}                 | ${""}
    ${"Toggle: on, Preference: system, System: dark"}          | ${{ dark_mode_ui_toggle: ON }}  | ${"system"} | ${"dark"}          | ${"system"}       | ${"dark"}                  | ${""}
    ${"Toggle: on, Preference: system, System: no-preference"} | ${{ dark_mode_ui_toggle: ON }}  | ${"system"} | ${"no-preference"} | ${"system"}       | ${"light"}                 | ${""}
  `(
    "$description: should report colorMode as $expectedColorMode, effectiveColorMode as $expectedEffectiveColorMode and cssClass as $expectedCssClass",
    ({
      featureFlags,
      uiColorMode,
      osColorMode,
      expectedColorMode,
      expectedEffectiveColorMode,
      expectedCssClass,
    }) => {
      vi.mocked(usePreferredColorScheme).mockReturnValue(
        computed(() => osColorMode)
      )

      const featureFlagStore = useFeatureFlagStore()

      featureFlagStore.toggleFeature(
        "dark_mode_ui_toggle",
        featureFlags.dark_mode_ui_toggle
      )

      // Set the user preference for color mode
      const uiStore = useUiStore()
      uiStore.colorMode = uiColorMode

      // Call the composable
      const { colorMode, effectiveColorMode, cssClass } = useDarkMode()

      // Assert the computed properties
      expect(colorMode.value).toBe(expectedColorMode)
      expect(effectiveColorMode.value).toBe(expectedEffectiveColorMode)
      expect(cssClass.value).toBe(expectedCssClass)
    }
  )
})
