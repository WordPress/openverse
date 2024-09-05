import { computed, useUiStore } from "#imports"

import { usePreferredColorScheme } from "@vueuse/core"

import { useFeatureFlagStore } from "~/stores/feature-flag"

export const DARK_MODE_CLASS = "dark-mode"
export const LIGHT_MODE_CLASS = "light-mode"

/**
 * Determines the dark mode setting based on user preference or feature flag.
 *
 * When dark mode toggling is disabled, the site is in "light mode".
 *
 * When the "dark_mode_ui_toggle" flag is enabled, the site will respect
 * the user system preference by default.
 *
 */
export function useDarkMode() {
  const uiStore = useUiStore()
  const featureFlagStore = useFeatureFlagStore()

  const darkModeToggleable = computed(() =>
    featureFlagStore.isOn("dark_mode_ui_toggle")
  )

  /**
   * the color mode setting for the app;
   *
   * This can be one of "dark", "light" or "system". If the toggle
   * feature is disabled, we default to "light".
   */
  const colorMode = computed(() => {
    if (darkModeToggleable.value) {
      return uiStore.colorMode
    }
    return "light"
  })

  /**
   * the color mode setting for the OS;
   *
   * This can be one of "dark" or "light". If the OS does not specify
   * a preference, we default to "light".
   */
  const osColorMode = computed(() => {
    const pref = usePreferredColorScheme()
    return pref.value === "no-preference" ? "light" : pref.value
  })

  /**
   * the effective color mode of the app;
   *
   * This can be one of "dark" or "light". This is a combination of the
   * toggle feature flag, the user's preference at the app and OS levels
   * and the default value of "light".
   */
  const effectiveColorMode = computed(() => {
    if (!darkModeToggleable.value) {
      return "light"
    }
    if (colorMode.value === "system") {
      return osColorMode.value
    }
    return colorMode.value
  })

  const cssClass = computed(() => {
    return {
      light: LIGHT_MODE_CLASS,
      dark: DARK_MODE_CLASS,
      system: "",
    }[colorMode.value]
  })

  return {
    colorMode,
    osColorMode,
    effectiveColorMode,
    cssClass,
  }
}
