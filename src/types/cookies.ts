import type { FeatureState } from '~/constants/feature-flag'

export type SnackbarState = 'not_shown' | 'visible' | 'dismissed'

/**
 * The cookies that Openverse uses to store the UI state.
 */
export interface OpenverseCookieState {
  /**
   * The state of the instructions snackbar for audio component.
   */
  uiInstructionsSnackbarState?: SnackbarState
  /**
   * Whether the filters were dismissed on desktop layout.
   */
  uiIsFilterDismissed?: boolean
  /**
   * Whether the site layout is desktop (or mobile).
   */
  uiIsDesktopLayout?: boolean
  /**
   * Whether the request user agent is mobile or not.
   */
  uiIsMobileUa?: boolean
  /**
   * The state of the feature flags.
   */
  features?: Record<string, FeatureState>
}
