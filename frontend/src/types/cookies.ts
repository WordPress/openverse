import type { FeatureState } from "~/constants/feature-flag"
import type { RealBreakpoint } from "~/constants/screens"
import type { BannerId } from "~/types/banners"

export type SnackbarState = "not_shown" | "visible" | "dismissed"

const baseCookieOptions = {
  path: "/",
  sameSite: "strict",
  secure: import.meta.env.DEPLOYMENT_ENV === "production",
} as const

export const persistentCookieOptions = {
  ...baseCookieOptions,
  maxAge: 60 * 60 * 24 * 60, // 60 days; Makes the cookie persistent.
} as const

export const sessionCookieOptions = {
  ...baseCookieOptions,
  maxAge: undefined, // these cookies are not persistent and will be deleted by the browser after the session.
} as const

/**
 * The cookies that Openverse uses to store the UI state.
 */
export interface OpenverseCookieState {
  ui: {
    /**
     * The state of the instructions snackbar for audio component.
     */
    instructionsSnackbarState?: SnackbarState
    /**
     * Whether the filters were dismissed on desktop layout.
     */
    isFilterDismissed?: boolean
    /**
     * The screen's max-width breakpoint.
     */
    breakpoint?: RealBreakpoint
    /**
     * Whether the request user agent is mobile or not.
     */
    isMobileUa?: boolean
    /**
     * The list of ids of dismissed banners.
     */
    dismissedBanners?: BannerId[]
  }
  /**
   * The state of the persistent feature flags.
   */
  features?: Record<string, FeatureState>
  /**
   * The state of the session-scoped feature flags.
   */
  sessionFeatures?: Record<string, FeatureState>
}
