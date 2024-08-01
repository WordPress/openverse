export const buttonForms = ["VLink", "button", "a"] as const

export type ButtonForm = (typeof buttonForms)[number]

export const baseButtonVariants = [
  "filled-pink-8",
  "filled-dark",
  "filled-gray",
  "filled-white",
  "bordered-white",
  "bordered-gray",
  "transparent-tx",
  "transparent-gray",
  "transparent-dark",
] as const
export type StandardButtonVariant = (typeof baseButtonVariants)[number]

export const buttonVariants = [
  ...baseButtonVariants,
  "plain",
  "plain--avoid",
] as const
export type ButtonVariant = (typeof buttonVariants)[number]

export const baseButtonSizes = ["large", "medium", "small"] as const
export type BaseButtonSize = (typeof baseButtonSizes)[number]

/**
 * `larger` is only used for the `VAudioControl` button component.
 */
export const buttonSizes = [...baseButtonSizes, "disabled", "larger"] as const
export type ButtonSize = (typeof buttonSizes)[number]

export const buttonTypes = ["button", "submit", "reset"] as const
export type ButtonType = (typeof buttonTypes)[number]

export const buttonConnections = ["start", "end", "top", "bottom"] as const
export type ButtonConnections = (typeof buttonConnections)[number]
