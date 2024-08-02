import { PRODUCTION, STAGING } from "~/constants/deploy-env"

const isProductionOrStaging = [PRODUCTION, STAGING].includes(
  import.meta.env.DEPLOYMENT_ENV
)
console.log(
  "setting up console utils, deployment env",
  import.meta.env.DEPLOYMENT_ENV
)

/**
 * Silence logging on the client when deployed
 */
export const getLogger = (level: "log" | "warn" | "error") =>
  isProductionOrStaging && import.meta.client
    ? () => {
        // do nothing
      }
    : console[level]

export const warn = getLogger("warn")
export const log = getLogger("log")
export const debug = getLogger("log")
export const error = getLogger("error")
