/*
 * Contains constants pertaining to errors that might arise in the application
 * that lead to the contents being replaced with an error message.
 */

export const NO_RESULT = "NO_RESULT"
export const SERVER_TIMEOUT = "SERVER_TIMEOUT"
export const ECONNABORTED = "ECONNABORTED"

export const ERR_UNKNOWN = "ERR_UNKNOWN"

export const customErrorCodes = [
  NO_RESULT,
  SERVER_TIMEOUT,
  ECONNABORTED,
  ERR_UNKNOWN,
] as const

export const ofetchErrorCodes = [
  "Too many results",
  "Request Timeout",
  "Conflict",
  "Too Early",
  "Too Many Requests",
  "Internal Server Error",
  "Bad Gateway",
  "Service Unavailable",
  "Gateway Timeout",
]

export const errorCodes = [...customErrorCodes, ...ofetchErrorCodes] as const

export const clientSideErrorCodes: readonly ErrorCode[] = [
  ECONNABORTED,
  SERVER_TIMEOUT,
  NO_RESULT,
  "ERR_NETWORK",
  "ETIMEDOUT",
] as const

export type ErrorCode = (typeof errorCodes)[number]
