import { consola } from "consola"

import { LOCAL, PRODUCTION, STAGING } from "~/constants/deploy-env"

/**
 * This logger is used only in the Nitro server.
 * Without the Nuxt context here, we cannot determine the deploymentEnv on the client,
 * which is necessary to silence logging on client in production.
 */
const logger = consola.withTag("Openverse")
// In production, `info`, in other environments - `debug`.
logger.level = [PRODUCTION, STAGING].includes(
  import.meta.env.DEPLOYMENT_ENV ?? LOCAL
)
  ? 3
  : 4

export { logger }
