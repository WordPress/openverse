export const isClient = process.client
export const defaultWindow = process.client ? window : undefined

// Each page should have an element with this `id` to make the skip-to-content work
export const skipToContentTargetId = "content"
