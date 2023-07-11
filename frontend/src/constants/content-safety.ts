/**
 * Contains constants pertaining to the content safety feature. These include
 * different types of sensitivities.
 */

export const USER_REPORTED = "user_reported_sensitive"
export const PROVIDER_SUPPLIED = "provider_supplied_sensitive"
export const TEXT_FILTERED = "sensitive_text"

export const SENSITIVITIES = [
  USER_REPORTED,
  PROVIDER_SUPPLIED,
  TEXT_FILTERED,
] as const

export type Sensitivity = (typeof SENSITIVITIES)[number]
