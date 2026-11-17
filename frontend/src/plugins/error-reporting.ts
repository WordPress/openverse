import { defineNuxtPlugin } from "#imports"

/**
 * Errors are logged rather than sent to a third-party service. On the server,
 * these logs end up in CloudWatch; on the client, only in the browser console.
 */
export default defineNuxtPlugin(() => ({
  provide: {
    captureException: (error: unknown, extra?: Record<string, unknown>) => {
      console.error(error, ...(extra ? [extra] : []))
    },
    captureMessage: (message: string) => {
      console.warn(message)
    },
  },
}))
