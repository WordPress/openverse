import { defineEventHandler } from "h3"

/**
 * A simple healthcheck that is always true.
 *
 * @todo Update to a resource-sensitive version that fails when
 * memory and/or cpu usage reach a configurable threshold.
 */
export default defineEventHandler((_) => {
  return "OK"
})
