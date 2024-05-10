import { useFeatureFlagStore } from "~/stores/feature-flag"

/**
 * TODO: Replace with the user's actual dark mode preference.
 * Eventually, dark mode detection will be based on user preference.
 * In testing, it reads the "force_dark_mode" feature flag
 */
export function useDarkMode() {
  const featureFlagStore = useFeatureFlagStore()
  const isDarkMode = featureFlagStore.isOn("force_dark_mode")
  return {
    isDarkMode,
    /** The CSS class representing the current color mode */
    cssClass: isDarkMode ? "dark-mode" : "light-mode",
  }
}
