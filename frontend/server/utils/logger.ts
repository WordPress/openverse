import { consola } from "consola"

const logger = consola.withTag("Openverse")
// In production, `info` on the server and silent on the client.
// In other environments, `debug`.
logger.level =
  process.env.NODE_ENV === "production" ? (import.meta.server ? 3 : -999) : 4

export { logger }
