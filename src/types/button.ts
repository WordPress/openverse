export const buttonForms = ['VLink', 'button'] as const

export type ButtonForm = typeof buttonForms[number]

export const buttonVariants = [
  'primary',
  'secondary',
  'secondary-bordered',
  'secondary-filled',
  'menu',
  'action-menu',
  'action-menu-bordered',
  'action-menu-bordered-pressed',
  'action-menu-muted',
  'action-menu-muted-pressed',
  'plain',
  'plain--avoid',
  'full',
] as const
export type ButtonVariant = typeof buttonVariants[number]

export const buttonSizes = ['large', 'medium', 'small', 'disabled'] as const
export type ButtonSize = typeof buttonSizes[number]

export const buttonTypes = ['button', 'submit', 'reset'] as const
export type ButtonType = typeof buttonTypes[number]

export const buttonConnections = ['start', 'end', 'none', 'all'] as const
export type ButtonConnections = typeof buttonConnections[number]
