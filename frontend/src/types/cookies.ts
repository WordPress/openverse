import type { FeatureState } from "~/constants/feature-flag"
import { isProd } from "~/utils/node-env"

import type { BannerId } from "~/types/banners"
import type { RealBreakpoint } from "~/constants/screens"

export type SnackbarState = "not_shown" | "visible" | "dismissed"

export const cookieOptions = {
  path: "/",
  sameSite: "strict",
  maxAge: 60 * 60 * 24 * 60, // 60 days
  secure: isProd,
}
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
