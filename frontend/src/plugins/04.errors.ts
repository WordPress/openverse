import { defineNuxtPlugin } from "#imports"

import { isAxiosError } from "axios"
import * as Sentry from "@sentry/nuxt"

import { ERR_UNKNOWN, ErrorCode, errorCodes } from "#shared/constants/errors"
import type { SupportedSearchType } from "#shared/constants/media"
import type { FetchingError, RequestKind } from "#shared/types/fetch-state"
import { debug } from "~/utils/console"

import type { NuxtApp } from "#app"
import type { FetchError } from "ofetch"

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
 * Checks the name rather than using `instanceof`, because the app and Nuxt
 * can use different copies of `ofetch`.
 */
const isFetchError = (error: unknown): error is FetchError =>
  error instanceof Error && error.name === "FetchError"

/**
 * Normalizes the errors from the Nuxt server proxy routes. The routes return
 * h3 errors, with the API's `detail` message or an error `code` in `data`.
 */
function normalizeProxyFetchError(
  error: FetchError,
  fetchingError: FetchingError
): FetchingError {
  const errorData = (error.data as { data?: unknown } | undefined)?.data as
    | { detail?: unknown; code?: unknown }
    | undefined

  if (error.statusCode) {
    fetchingError.statusCode = error.statusCode
  } else {
    // The request didn't receive a response.
    fetchingError.code = "ERR_NETWORK"
  }
  if (typeof errorData?.code === "string" && isValidErrorCode(errorData.code)) {
    fetchingError.code = errorData.code
  }

  const retryAfter = error.response?.headers.get("retry-after")
  if (retryAfter) {
    fetchingError.details = { ...fetchingError.details, retryAfter }
  }

  fetchingError.message =
    typeof errorData?.detail === "string" ? errorData.detail : error.message
  return fetchingError
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
export function normalizeFetchingError(
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

  if (isFetchError(error)) {
    return normalizeProxyFetchError(error, fetchingError)
  }

  if (!isAxiosError(error)) {
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
 * @param originalError - the original error, usually an AxiosError
 * @param fetchingError - the normalized error object
 * @param nuxtApp - the context object
 */
export function recordError(
  originalError: unknown,
  fetchingError: FetchingError,
  nuxtApp: NuxtApp
) {
  debug("Recording fetching error", fetchingError)
  if (fetchingError.statusCode === 429) {
    // These are more readily monitored via the Cloudflare dashboard.
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
     *    number of 404 responses from the frontend server that could indicate a frontend
     *    implementation or configuration error suddenly causing malformed
     *    identifiers to be used. Neither Sentry nor Plausible are the right tool
     *    for that task. If the 404s are caused by an API issue, we'd see that in
     *    API response code monitoring, where we can more easily trace the cause
     */
    return
  }

  if (import.meta.client && fetchingError.code === "ERR_NETWORK") {
    /**
     * Record network errors in Plausible so that we can evaluate potential
     * regional or device configuration issues, for which Sentry is not
     * as good a tool. Additionally, the number of these events are trivial
     * for Plausible, but do actually affect our Sentry quota enough that it
     * is worth diverting them.
     */
    const { $sendCustomEvent } = nuxtApp
    $sendCustomEvent("NETWORK_ERROR", {
      requestKind: fetchingError.requestKind,
      searchType: fetchingError.searchType,
    })
  } else {
    Sentry.captureException(originalError, { extra: { fetchingError } })
  }
}

export default defineNuxtPlugin(async (nuxtApp) => {
  function processFetchingError(
    ...[originalError, ...args]: Parameters<typeof normalizeFetchingError>
  ) {
    const fetchingError = normalizeFetchingError(originalError, ...args)
    recordError(originalError, fetchingError, nuxtApp as NuxtApp)
    return fetchingError
  }

  return {
    provide: {
      processFetchingError,
    },
  }
})
