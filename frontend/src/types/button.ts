export const buttonForms = ["VLink", "button"] as const

export type ButtonForm = (typeof buttonForms)[number]

export const buttonVariants = [
  "plain",
  "plain--avoid",
  "dropdown-label",
  "dropdown-label-pressed",
  "filled-pink",
  "filled-dark",
  "filled-gray",
  "filled-white",
  "filled-transparent",
  "bordered-white",
  "bordered-gray",
  "transparent-tx",
  "transparent-gray",
  "transparent-dark",
] as const
export type ButtonVariant = (typeof buttonVariants)[number]

export const buttonSizes = ["large", "medium", "small", "disabled"] as const
export type ButtonSize = (typeof buttonSizes)[number]

export const buttonTypes = ["button", "submit", "reset"] as const
export type ButtonType = (typeof buttonTypes)[number]

export const buttonConnections = ["start", "end", "none", "all"] as const
export type ButtonConnections = (typeof buttonConnections)[number]
