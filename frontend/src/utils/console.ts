/**
 * Silence logging on the client in production and on staging.
 */
export const getLogger = (level: "log" | "warn" | "error") => {
  if (import.meta.server) {
    return console[level]
  }
  return () => {
    // do nothing
  }
}

export const warn = getLogger("warn")
export const log = getLogger("log")
export const debug = getLogger("log")
