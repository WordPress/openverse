import type { FeatureState } from "~/constants/feature-flag"
import { isProd } from "~/utils/node-env"

import type { BannerId } from "~/types/banners"
import type { Breakpoint } from "~/constants/screens"

import type { CookieSerializeOptions } from "cookie"

export type SnackbarState = "not_shown" | "visible" | "dismissed"

export const cookieOptions: CookieSerializeOptions = {
  path: "/",
  sameSite: "strict",
  maxAge: 60 * 60 * 24 * 60, // 60 days
  secure: isProd,
}
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
   * The screen's max-width breakpoint.
   */
  uiBreakpoint?: Breakpoint
  /**
   * Whether the request user agent is mobile or not.
   */
  uiIsMobileUa?: boolean
  /**
   * The list of ids of dismissed banners.
   */
  uiDismissedBanners?: BannerId[]
  /**
   * The state of the feature flags.
   */
  features?: Record<string, FeatureState>
}
