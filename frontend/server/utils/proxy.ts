import {
  createError,
  getQuery,
  getRequestHeader,
  getRouterParam,
  setResponseHeader,
  type H3Event,
} from "h3"

import {
  isSupportedMediaType,
  type SupportedMediaType,
} from "#shared/constants/media"
import {
  INTERNAL_REQUEST_HEADER,
  RELATED_QUERY_ALLOWLIST,
  SEARCH_QUERY_ALLOWLIST,
} from "#shared/constants/proxy"
import { mediaSlug, validateUUID } from "#shared/utils/query-utils"
import type { Events } from "#shared/types/analytics"

import type { OpenverseClient } from "@openverse/api-client"

export type ProxyRequestKind = "search" | "single-result" | "related"

export type SearchTimeEventPayload = Events["SEARCH_RESPONSE_TIME"]

const QUERY_ALLOWLISTS: Record<ProxyRequestKind, readonly string[]> = {
  search: SEARCH_QUERY_ALLOWLIST,
  "single-result": [],
  related: RELATED_QUERY_ALLOWLIST,
}

const notFound = () =>
  createError({ statusCode: 404, statusMessage: "Not Found" })

/**
 * Keeps only the string values of the allowed query parameters, so that the
 * proxy can't be used to send other parameters, such as `page_size`, with the
 * frontend's credentials.
 */
export const filterQuery = (
  query: Record<string, unknown>,
  allowlist: readonly string[]
): Record<string, string> => {
  const filtered: Record<string, string> = {}
  for (const key of allowlist) {
    const value = query[key]
    if (typeof value === "string") {
      filtered[key] = value
    }
  }
  return filtered
}

/**
 * Validates the route params so that the proxy routes can only reach the
 * search, single result and related media endpoints of the API.
 */
export const validateRequest = (event: H3Event, kind: ProxyRequestKind) => {
  const mediaType = getRouterParam(event, "type")
  if (!mediaType || !isSupportedMediaType(mediaType)) {
    throw notFound()
  }

  let id: string | undefined
  if (kind !== "search") {
    id = getRouterParam(event, "id")
    if (!validateUUID(id)) {
      throw notFound()
    }
  }

  return {
    mediaType,
    id,
    query: filterQuery(getQuery(event), QUERY_ALLOWLISTS[kind]),
  }
}

/**
 * Returns the API schema path for the request, with an `{identifier}`
 * placeholder for the media id. For example, `related` for `image` returns
 * `/v1/images/{identifier}/related/`.
 */
export const generateApiPath = (
  kind: ProxyRequestKind,
  mediaType: SupportedMediaType
) => {
  const slug = mediaSlug(mediaType)
  switch (kind) {
    case "search": {
      return `/v1/${slug}/`
    }
    case "single-result": {
      return `/v1/${slug}/{identifier}/`
    }
    case "related": {
      return `/v1/${slug}/{identifier}/related/`
    }
  }
}

/**
 * `OpenverseClient.GET` is typed for each schema path, and the proxy chooses
 * the path at runtime. The query parameters are validated by `filterQuery`.
 */
type ProxyGet = (
  path: string,
  init: {
    params: { path?: { identifier: string }; query?: Record<string, string> }
  }
) => Promise<{ data?: unknown; error?: unknown; response: Response }>

const getFromApi = (
  apiClient: OpenverseClient,
  kind: ProxyRequestKind,
  mediaType: SupportedMediaType,
  id: string | undefined,
  query: Record<string, string>
) =>
  (apiClient.GET as unknown as ProxyGet)(generateApiPath(kind, mediaType), {
    params: { path: id ? { identifier: id } : undefined, query },
  })

/**
 * Builds the SEARCH_RESPONSE_TIME analytics event payload from the API
 * response headers. Returns `undefined` if the response did not pass through
 * Cloudflare, for example, when Nitro uses the internal API address.
 */
export const buildEventPayload = (
  headers: Headers,
  requestDatetime: Date,
  mediaType: SupportedMediaType,
  query: Record<string, string>
): SearchTimeEventPayload | undefined => {
  const date = headers.get("date")
  const cfCacheStatus = headers.get("cf-cache-status")
  const cfRayIATA = headers.get("cf-ray")?.split("-")[1]
  if (!date || !cfCacheStatus || !cfRayIATA) {
    return
  }

  const responseDatetime = new Date(date)
  if (responseDatetime < requestDatetime) {
    return
  }

  const search = new URLSearchParams(query).toString()
  return {
    cfCacheStatus,
    cfRayIATA,
    elapsedTime: Math.floor(
      (responseDatetime.getTime() - requestDatetime.getTime()) / 1000
    ),
    queryString: search ? `?${search}` : "",
    mediaType,
  }
}

const isTimeoutError = (error: unknown) => {
  const { name, cause } = error as { name?: string; cause?: { name?: string } }
  return name === "TimeoutError" || cause?.name === "TimeoutError"
}

/**
 * Whether the request is an in-process SSR request, whose page load has
 * already been counted by the rate limits.
 */
export const isInternalRequest = (event: H3Event) => {
  const token = event.context.internalRequestToken
  return (
    Boolean(token) && getRequestHeader(event, INTERNAL_REQUEST_HEADER) === token
  )
}

/**
 * Forwards the request to the API with the frontend's credentials. The
 * browser's cookies and headers are not forwarded.
 *
 * API errors are returned with the API's status code and `detail` message.
 * Timeouts return 504 and other failures, including a failed API token
 * request, return 502.
 */
export const proxyApiRequest = async (
  event: H3Event,
  kind: ProxyRequestKind
) => {
  const { apiClient } = event.context
  if (!apiClient) {
    throw createError({
      statusCode: 500,
      statusMessage: "The Openverse API client is not initialized.",
    })
  }

  const { mediaType, id, query } = validateRequest(event, kind)
  const requestDatetime = new Date()

  let result: Awaited<ReturnType<typeof getFromApi>>
  try {
    result = await getFromApi(apiClient, kind, mediaType, id, query)
  } catch (error) {
    const isTimeout = isTimeoutError(error)
    throw createError({
      statusCode: isTimeout ? 504 : 502,
      data: { code: isTimeout ? "ECONNABORTED" : "ERR_BAD_RESPONSE" },
    })
  }

  const { data, error, response } = result
  if (!response.ok) {
    const retryAfter = Number(response.headers.get("retry-after"))
    if (retryAfter > 0) {
      setResponseHeader(event, "Retry-After", retryAfter)
    }
    const detail = (error as { detail?: unknown } | undefined)?.detail
    throw createError({
      statusCode: response.status,
      data: typeof detail === "string" ? { detail } : undefined,
    })
  }

  if (kind === "search") {
    return {
      eventPayload: buildEventPayload(
        response.headers,
        requestDatetime,
        mediaType,
        query
      ),
      data,
    }
  }
  return data
}
