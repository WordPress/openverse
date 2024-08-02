import { computed } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"

export const DARK_MODE_CLASS = "dark-mode"
export const LIGHT_MODE_CLASS = "light-mode"

/**
 * TODO: Replace with the user's actual dark mode preference.
 * Dark mode detection will be based on user preference,
 * overwritten by the "force_dark_mode" feature flag.
 */
export function useDarkMode() {
  const featureFlagStore = useFeatureFlagStore()

  const isDarkMode = computed(() => featureFlagStore.isOn("force_dark_mode"))
  const cssClass = computed(() =>
    isDarkMode.value ? DARK_MODE_CLASS : LIGHT_MODE_CLASS
  )

  return {
    isDarkMode,
    /** The CSS class representing the current color mode. */
    cssClass,
  }
}
