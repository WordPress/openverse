import axios from "axios"
import { Plugin, Context } from "@nuxt/types"

import { ERR_UNKNOWN, ErrorCode, errorCodes } from "~/constants/errors"
import type { FetchingError, RequestKind } from "~/types/fetch-state"
import type { SupportedSearchType } from "~/constants/media"

import { useAnalytics } from "~/composables/use-analytics"

const isValidErrorCode = (
  code: string | undefined | null
): code is ErrorCode => {
  if (!code) {
    return false
  }
  return (errorCodes as readonly string[]).includes(code)
}

function isDetailedResponseData(data: unknown): data is { detail: string } {
  return !!data && typeof data === "object" && "detail" in data
}

/**
 * Normalize any error occurring during a network call.
 *
 * @param error - Any error arising during a network call
 * @param searchType - The type of search selected when the error occurred
 * @param requestKind - The kind of request the error occurred for
 * @param details - Any additional details to attach to the error
 * @returns Normalized error object
 */
function normalizeFetchingError(
  error: unknown,
  searchType: SupportedSearchType,
  requestKind: RequestKind,
  details?: Record<string, string>
): FetchingError {
  const fetchingError: FetchingError = {
    requestKind,
    details,
    searchType,
    code: ERR_UNKNOWN,
  }

  if (!axios.isAxiosError(error)) {
    fetchingError.message = (error as Error).message
    return fetchingError
  }

  // Otherwise, it's an AxiosError
  if (isValidErrorCode(error.code)) {
    fetchingError.code = error.code
  }

  if (error.response?.status) {
    fetchingError.statusCode = error.response.status
  }

  const responseData = error?.response?.data

  // Use the message returned by the API.
  if (isDetailedResponseData(responseData)) {
    fetchingError.message = responseData.detail as string
  } else {
    fetchingError.message = error.message
  }

  return fetchingError
}

/**
 * Record network errors using the appropriate tool, as needed,
 * based on response code, status, and request kind.
 * @param error - The error to record
 */
function recordError(
  context: Context,
  originalError: unknown,
  fetchingError: FetchingError
) {
  if (fetchingError.code === "ERR_NETWORK") {
    /**
     * Record network errors in Plausible so that we can evaluate potential
     * regional or device configuration issues, for which Sentry is not
     * as good a tool. Additionally, the number of these events are trivial
     * for Plausible, but do actually affect our Sentry quota enough that it
     * is worth diverting them.
     */
    context.$sendCustomEvent("NETWORK_ERROR", {
      requestKind: fetchingError.requestKind,
      searchType: fetchingError.searchType,
    })

    return
  }

  if (
    fetchingError.requestKind === "single-result" &&
    fetchingError.statusCode === 404
  ) {
    /**
     * Do not record 404s for single result requests because:
     * 1. Plausible will already record them as resulting in a 404 page view
     * 2. The Openverse API 404s on malformed identifiers, so there is no way
     *    to distinguish between truly not found works and bad requests from
     *    the client side.
     * 3. There isn't much we can do other than monitor for an anomalously high
     *    number of 404 responses from the frontend that could indicate a frontend
     *    implementation or configuration error suddenly causing malformed
     *    identifiers to be used. Neither Sentry nor Plausible are the right tool
     *    for that task.
     */
    return
  }

  context.$sentry.captureException(originalError, { extra: { fetchingError } })
}

function createProcessFetchingError(
  context: Context
): typeof normalizeFetchingError {
  function processFetchingError(
    ...[originalError, ...args]: Parameters<typeof normalizeFetchingError>
  ) {
    const fetchingError = normalizeFetchingError(originalError, ...args)
    recordError(context, originalError, fetchingError)
    return fetchingError
  }

  return processFetchingError
}

declare module "@nuxt/types" {
  interface Context {
    $processFetchingError: ReturnType<typeof createProcessFetchingError>
  }
}

const plugin: Plugin = async (context, inject) => {
  inject("processFetchingError", createProcessFetchingError(context))
}

export default plugin
