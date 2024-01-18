import { FetchError } from "ofetch"

import {
  clientSideErrorCodes,
  ERR_UNKNOWN,
  NO_RESULT,
} from "~/constants/errors"
import type { FetchingError, RequestKind } from "~/types/fetch-state"
import type { SupportedSearchType } from "~/constants/media"

/**
 * Parses an error object to standardize error-related details for the frontend.
 * @param error - the error object to parse.
 * @param searchType - the type of media that request was made for (can be `all content`).
 * @param requestKind - the kind of request that was made.
 * @param details - additional data to display on the error page, e.g. searchTerm.
 */
export const parseFetchingError = (
  error: unknown,
  searchType: SupportedSearchType,
  requestKind: RequestKind,
  details?: Record<string, string>
) => {
  const fetchingError: FetchingError = {
    requestKind,
    details,
    searchType,
    code: ERR_UNKNOWN,
  }
  if (error instanceof FetchError) {
    fetchingError.statusCode = error.statusCode
    fetchingError.message = error.message
  }
  return fetchingError
}

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

export const handledClientSide = (error: FetchingError | null) => {
  return (
    error &&
    !isNonRetryableErrorStatusCode(error.statusCode) &&
    (clientSideErrorCodes as readonly string[]).includes(error.code)
  )
}
