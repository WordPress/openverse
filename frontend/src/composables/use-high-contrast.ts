import { computed, ref, onMounted, watchEffect } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useDarkMode } from "~/composables/use-dark-mode"

export const HIGH_CONTRAST_LIGHT_MODE_CLASS = "high-contrast-light-mode"
export const HIGH_CONTRAST_DARK_MODE_CLASS = "high-contrast-dark-mode"

/**
 * Determines the high contrast mode setting based on user preference or OS setting.
 *
 * When the "high_contrast_ui_toggle" flag is enabled, the site will respect
 * the user's system preference for high contrast by default (using prefers-contrast media query).
 *
 * The high contrast mode works in combination with the color mode (light/dark) to provide
 * four possible visual themes:
 * - Light mode (normal contrast)
 * - Light mode (high contrast)
 * - Dark mode (normal contrast)
 * - Dark mode (high contrast)
 */
export function useHighContrast() {
  const uiStore = useUiStore()
  const featureFlagStore = useFeatureFlagStore()
  const { effectiveColorMode } = useDarkMode()

  const highContrastToggleable = computed(() =>
    featureFlagStore.isOn("high_contrast_ui_toggle")
  )

  /**
   * Detect OS-level preference for high contrast using the prefers-contrast media query.
   * Returns true if the user has requested more contrast at the OS level.
   */
  const osHighContrast = ref(false)

  onMounted(() => {
    // Check if the browser supports the prefers-contrast media query
    const mediaQuery = window.matchMedia("(prefers-contrast: more)")
    osHighContrast.value = mediaQuery.matches

    // Listen for changes to the OS high contrast preference
    const handleChange = (e: MediaQueryListEvent) => {
      osHighContrast.value = e.matches
    }
    mediaQuery.addEventListener("change", handleChange)

    // Note: cleanup is handled by Vue's lifecycle
  })

  /**
   * The contrast mode setting for the app.
   *
   * This can be one of "normal", "high", or "system". If the toggle
   * feature is disabled, we default to "normal".
   */
  const contrastMode = computed(() => {
    if (highContrastToggleable.value) {
      return uiStore.contrastMode
    }
    return "normal"
  })

  /**
   * The effective contrast mode of the app.
   *
   * This can be one of "normal" or "high". This is a combination of the
   * toggle feature flag, the user's preference at the app and OS levels,
   * and the default value of "normal".
   */
  const effectiveContrastMode = computed(() => {
    if (!highContrastToggleable.value) {
      return "normal"
    }
    if (contrastMode.value === "system") {
      return osHighContrast.value ? "high" : "normal"
    }
    return contrastMode.value
  })

  /**
   * Whether high contrast mode is currently active (either explicitly set or via OS preference).
   */
  const isHighContrast = computed(() => effectiveContrastMode.value === "high")

  /**
   * The CSS class to apply to the body element based on the contrast and color mode.
   * Returns a class that combines both the color mode and contrast mode.
   *
   * - high-contrast-light-mode: High contrast + light theme
   * - high-contrast-dark-mode: High contrast + dark theme
   * - Empty string: Normal contrast (handled by color mode classes)
   */
  const cssClass = computed(() => {
    if (effectiveContrastMode.value !== "high") {
      return ""
    }

    // When high contrast is enabled, we need to combine it with the current color mode
    return effectiveColorMode.value === "dark"
      ? HIGH_CONTRAST_DARK_MODE_CLASS
      : HIGH_CONTRAST_LIGHT_MODE_CLASS
  })

  /**
   * The server does not have access to media queries, so the `system` contrast mode
   * defaults to "normal" on the server.
   */
  const serverContrastMode = computed(() => {
    return !highContrastToggleable.value || contrastMode.value === "system"
      ? "normal"
      : contrastMode.value
  })

  return {
    contrastMode,
    osHighContrast,
    effectiveContrastMode,
    isHighContrast,
    serverContrastMode,
    cssClass,
  }
}
