import { defineEventHandler } from "h3"

/**
 * A simple healthcheck that is always true and confirms the server is running.
 */
export default defineEventHandler(() => {
  return "OK"
})
