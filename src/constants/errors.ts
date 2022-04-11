/*
 * Contains constants pertaining to errors that might arise in the application
 * that lead to the contents being replaced with an error message.
 */

export const NO_RESULT = 'NO_RESULT'
export const SERVER_TIMEOUT = 'SERVER_TIMEOUT'

export const errorCodes = [NO_RESULT, SERVER_TIMEOUT] as const

export type ErrorCode = typeof errorCodes[number]
