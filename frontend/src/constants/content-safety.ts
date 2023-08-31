/**
 * Contains constants pertaining to the content safety feature. These include
 * different types of sensitivities.
 */

// Reasons why a piece of media is designated sensitive
export const USER_REPORTED = "user_reported_sensitive"
export const PROVIDER_SUPPLIED = "provider_supplied_sensitive"
export const TEXT_FILTERED = "sensitive_text"

export const SENSITIVITIES = [
  USER_REPORTED,
  PROVIDER_SUPPLIED,
  TEXT_FILTERED,
] as const

export type Sensitivity = (typeof SENSITIVITIES)[number]

// Various UI states of a piece of media, sensitive or otherwise
export const NON_SENSITIVE = "non-sensitive"
export const SENSITIVE_HIDDEN = "sensitive-hidden"
export const SENSITIVE_SHOWN = "sensitive-shown"
export const SENSITIVE_MEDIA_STATES = [
  NON_SENSITIVE,
  SENSITIVE_HIDDEN,
  SENSITIVE_SHOWN,
] as const

export type SensitiveMediaVisibility = (typeof SENSITIVE_MEDIA_STATES)[number]

export const INCLUDE_SENSITIVE_QUERY_PARAM =
  "unstable__include_sensitive_results"
export const SENSITIVITY_RESPONSE_PARAM = "unstable__sensitivity"
