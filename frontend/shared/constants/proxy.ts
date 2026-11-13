/**
 * The prefix of the Nitro routes that proxy requests to the Openverse API.
 */
export const PROXY_ROUTE_PREFIX = "/api/"

/**
 * The header that marks the in-process SSR requests to the proxy routes.
 * Its value is a random token that only the Nitro process knows, so a client
 * cannot use it to skip the rate limits.
 */
export const INTERNAL_REQUEST_HEADER = "x-ov-internal-request"

/**
 * The query parameters that the frontend sends to the search endpoints.
 * The proxy drops all others, including `page_size`, so that visitors don't
 * get the larger page size that authenticated requests allow.
 */
export const SEARCH_QUERY_ALLOWLIST = [
  "q",
  "page",
  "license",
  "license_type",
  "extension",
  "size",
  "aspect_ratio",
  "category",
  "source",
  "length",
  "peaks",
  "unstable__include_sensitive_results",
  "collection",
  "unstable__collection",
  "tag",
  "unstable__tag",
  "creator",
] as const

export const RELATED_QUERY_ALLOWLIST = ["peaks"] as const
