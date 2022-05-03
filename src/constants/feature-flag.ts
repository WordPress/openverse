export const ENABLED = 'enabled'
export const DISABLED = 'disabled'
export const SWITCHABLE = 'switchable'

export const FLAG_STATUSES = [ENABLED, DISABLED, SWITCHABLE] as const

export type FlagStatus = typeof FLAG_STATUSES[number]

export const ON = 'on'
export const OFF = 'off'

export const FEATURE_STATES = [ON, OFF] as const

export type FeatureState = typeof FEATURE_STATES[number]
