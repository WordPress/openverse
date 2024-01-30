import { clientSideErrorCodes, NO_RESULT } from "~/constants/errors"
import type { FetchingError } from "~/types/fetch-state"

const NON_RETRYABLE_ERROR_CODES = [429, 500, 404] as const
const isNonRetryableErrorStatusCode = (statusCode: number | undefined) => {
  return (
    statusCode &&
    (NON_RETRYABLE_ERROR_CODES as readonly number[]).includes(statusCode)
  )
}

/**
 * Returns true if the request should be retried if error occurred on
 * the server. For 429, 500 or 404 errors, or for NO_RESULT error,
 * the status will not change on retry, so the request should not be resent.
 * TODO: Update this function with other error codes if needed.
 */
export const isRetriable = (error: FetchingError) => {
  const { statusCode, code } = error
  return !(isNonRetryableErrorStatusCode(statusCode) || code === NO_RESULT)
}

export const handledClientSide = (error: FetchingError) => {
  return (
    !isNonRetryableErrorStatusCode(error.statusCode) &&
    (clientSideErrorCodes as readonly string[]).includes(error.code)
  )
}
