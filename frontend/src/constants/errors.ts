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

/**
 * The error codes Axios uses.
 * @see https://github.com/axios/axios/blob/9588fcdec8aca45c3ba2f7968988a5d03f23168c/lib/core/AxiosError.js#L57C2-L71
 */
const axiosErrorCodes = [
  "ERR_BAD_OPTION_VALUE",
  "ERR_BAD_OPTION",
  "ECONNABORTED",
  "ETIMEDOUT",
  "ERR_NETWORK",
  "ERR_FR_TOO_MANY_REDIRECTS",
  "ERR_DEPRECATED",
  "ERR_BAD_RESPONSE",
  "ERR_BAD_REQUEST",
  "ERR_CANCELED",
  "ERR_NOT_SUPPORT",
  "ERR_INVALID_URL",
] as const

export const errorCodes = [...customErrorCodes, ...axiosErrorCodes] as const

export const clientSideErrorCodes: readonly ErrorCode[] = [
  ECONNABORTED,
  SERVER_TIMEOUT,
  NO_RESULT,
  "ERR_NETWORK",
  "ETIMEDOUT",
] as const

export type ErrorCode = (typeof errorCodes)[number]
