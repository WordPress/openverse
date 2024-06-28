const isProd = import.meta.env.NODE_ENV === "production"

export const getLogger = (level: "log" | "warn" | "error") =>
  isProd && import.meta.client
    ? () => {
        // do nothing
      }
    : console[level]

export const warn = getLogger("warn")
export const log = getLogger("log")
export const debug = getLogger("log")
export const error = getLogger("error")
