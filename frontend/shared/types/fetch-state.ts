import type { ErrorCode } from "#shared/constants/errors"
import type { SupportedSearchType } from "#shared/constants/media"

/**
 * Describes the kind of API request that was made.
 */
export type RequestKind = "search" | "single-result" | "related" | "provider"

/**
 * This interface represents errors related to data-fetching from the API.
 * It has the information that can be used on the error page.
 */
export interface FetchingError {
  statusCode?: number
  statusMessage?: string
  message?: string
  /**
   * Axios error codes or custom error code like NO_RESULT.
   * @see frontend/src/constants/errors.ts
   */
  code: ErrorCode
  requestKind: RequestKind
  searchType: SupportedSearchType
  /**
   * Additional details about the error, e.g. the search term.
   */
  details?: Record<string, string>
}

export type FetchState =
  | { status: "idle" | "fetching" | "success"; error: null }
  | { status: "error"; error: FetchingError }
