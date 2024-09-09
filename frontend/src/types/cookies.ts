import type { FeatureState } from "~/constants/feature-flag"
import { UiState } from "~/stores/ui"

const baseCookieOptions = {
  path: "/",
  sameSite: "strict",
  secure: true,
} as const

export const persistentCookieOptions = {
  ...baseCookieOptions,
  maxAge: 60 * 60 * 24 * 60, // 60 days; Makes the cookie persistent.
} as const

export const defaultPersistientCookieState: OpenverseCookieState = {
  ui: {
    colorMode: "system",
  },
}

export const sessionCookieOptions = {
  ...baseCookieOptions,
  maxAge: undefined, // these cookies are not persistent and will be deleted by the browser after the session.
} as const

/**
 * The cookies that Openverse uses to store the UI state.
 */
export interface OpenverseCookieState {
  /**
   * Values used to SSR the site,
   * persisted by the ui store.
   */
  ui: Partial<UiState>
  /**
   * The state of the persistent feature flags.
   */
  features?: Record<string, FeatureState>
  /**
   * The state of the session-scoped feature flags.
   */
  sessionFeatures?: Record<string, FeatureState>
}
