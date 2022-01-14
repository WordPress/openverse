export const isClient = typeof window !== 'undefined'
export const defaultWindow = isClient ? window : undefined
