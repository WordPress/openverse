import { decodeMediaData, useRuntimeConfig } from "#imports"

import axios, { AxiosRequestConfig, AxiosResponse } from "axios"

import { debug, warn } from "~/utils/console"

import { mediaSlug } from "~/utils/query-utils"
import { AUDIO, SupportedMediaType } from "~/constants/media"
import type { Events } from "~/types/analytics"
import type { Media } from "~/types/media"
import type {
  PaginatedCollectionQuery,
  PaginatedSearchQuery,
} from "~/types/search"

const DEFAULT_REQUEST_TIMEOUT = 30000

export type SearchTimeEventPayload = Events["SEARCH_RESPONSE_TIME"]

/**
 * @param errorCondition - if true, the `message` warning is logged in the console
 * @param message - message to display if there is an error in request
 * @param config - Axios config object that containing request url
 */
const validateRequest = (
  errorCondition: boolean,
  message: string,
  config: AxiosRequestConfig
): void => {
  if (errorCondition) {
    warn(
      `There is a problem with the request url: ${message}.
Please check the url: ${config.baseURL}${config.url}`
    )
  }
}

export interface MediaResult<
  T extends Media | Media[] | Record<string, Media>,
> {
  result_count: number
  page_count: number
  page_size: number
  page: number
  results: T
}

const userAgent =
  "Openverse/0.1 (https://openverse.org; openverse@wordpress.org)"
/**
 * Decodes the text data to avoid encoding problems.
 * Also, converts the results from an array of media
 * objects into an object with media id as keys.
 * @param mediaType - the media type of the search query
 * @param data - search result data
 * @param fakeSensitive - whether to fake sensitive data for testing
 */
function transformResults<T extends Media>(
  mediaType: SupportedMediaType,
  data: MediaResult<T[]>,
  fakeSensitive: boolean
): MediaResult<Record<string, T>> {
  const mediaResults = <T[]>data.results ?? []
  return {
    ...data,
    results: mediaResults.reduce(
      (acc, item) => {
        acc[item.id] = decodeMediaData(item, mediaType, fakeSensitive)
        return acc
      },
      {} as Record<string, T>
    ),
  }
}

/**
 * Processes AxiosResponse from a search query to construct
 * SEARCH_RESPONSE_TIME analytics event payload.
 * @param response - Axios response
 * @param requestDatetime - datetime before request was sent
 * @param mediaType - the media type of the search query
 */
const buildEventPayload = (
  response: AxiosResponse,
  requestDatetime: Date,
  mediaType: SupportedMediaType
): SearchTimeEventPayload | undefined => {
  const REQUIRED_HEADERS = ["date", "cf-cache-status", "cf-ray"]

  const responseHeaders = response.headers
  if (!REQUIRED_HEADERS.every((header) => header in responseHeaders)) {
    return
  }

  const responseDatetime = new Date(responseHeaders["date"])
  if (responseDatetime < requestDatetime) {
    // response returned was from the local cache
    return
  }

  const cfRayIATA = responseHeaders["cf-ray"].split("-")[1]
  if (cfRayIATA === undefined) {
    return
  }

  const elapsedSeconds = Math.floor(
    (responseDatetime.getTime() - requestDatetime.getTime()) / 1000
  )

  const responseUrl =
    response.request?.responseURL ?? response.request?.res?.responseUrl
  if (!responseUrl) {
    return
  }
  const url = new URL(responseUrl)

  return {
    cfCacheStatus: responseHeaders["cf-cache-status"].toString(),
    cfRayIATA: cfRayIATA.toString(),
    elapsedTime: elapsedSeconds,
    queryString: url.search,
    mediaType: mediaType,
  }
}

/**
 * The list of options that can be passed when instantiating a new API service.
 */
export interface ApiServiceConfig {
  /** to use a different base URL than configured for the environment */
  baseUrl?: string
  /** to make authenticated requests to the API */
  accessToken?: string
  /** whether to use the `'v1/'` prefix after the base URL */
  isVersioned?: boolean
  /** whether to use fake sensitivity data for testing */
  fakeSensitive?: boolean
}

export const createApiClient = ({
  accessToken = undefined,
  isVersioned = true,
  fakeSensitive = false,
}: ApiServiceConfig = {}) => {
  const baseUrl =
    useRuntimeConfig().public.apiUrl ?? "https://api.openverse.org/"

  const headers: AxiosRequestConfig["headers"] = {}
  if (import.meta.server) {
    headers["User-Agent"] = userAgent
  }
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`
  }
  const axiosParams: AxiosRequestConfig = {
    baseURL: isVersioned ? `${baseUrl}v1/` : baseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
    headers,
  }

  const client = axios.create(axiosParams)
  client.interceptors.request.use(function (config) {
    validateRequest(
      !config.url?.endsWith("/"),
      "API request urls should have a trailing slash",
      config as AxiosRequestConfig
    )
    validateRequest(
      config.url?.includes("//") ?? false,
      "API request urls should not have two slashes",
      config as AxiosRequestConfig
    )
    return config
  })
  client.interceptors.response.use(
    (response) => {
      debug(
        response.request.res?.responseUrl ?? response.request.responseURL,
        response.status
      )
      return response
    },
    (error) => {
      if (error.code === "ECONNABORTED") {
        error.message = `timeout of ${
          DEFAULT_REQUEST_TIMEOUT / 1000
        } seconds exceeded`
      }
      debug("error:", error.message)
      return Promise.reject(error)
    }
  )

  const search = async <T extends Media>(
    mediaType: SupportedMediaType,
    query: PaginatedSearchQuery | PaginatedCollectionQuery
  ) => {
    // Add the `peaks` param to all audio searches automatically
    if (mediaType === AUDIO) {
      query.peaks = "true"
    }
    const requestDatetime = new Date()
    const res = await client.get<MediaResult<T[]>>(`${mediaSlug(mediaType)}/`, {
      params: query,
    })
    const eventPayload = buildEventPayload(res, requestDatetime, mediaType)

    return {
      eventPayload,
      data: transformResults(mediaType, res.data, fakeSensitive),
    }
  }

  const getSingleMedia = async <T extends Media>(
    mediaType: SupportedMediaType,
    id: string
  ) => {
    const res = await client.get<T>(`${mediaSlug(mediaType)}/${id}/`)
    return decodeMediaData(res.data, mediaType)
  }

  const getRelatedMedia = async (mediaType: SupportedMediaType, id: string) => {
    const params = mediaType === AUDIO ? { peaks: "true" } : {}
    const res = await client.get<{ results: Media[] }>(
      `${mediaSlug(mediaType)}/${id}/related/`,
      { params }
    )
    return res.data.results.map((media) => decodeMediaData(media, mediaType))
  }

  const stats = async (mediaType: SupportedMediaType) => {
    const res = await client.get(`${mediaSlug(mediaType)}/stats/`)
    return res.data
  }

  return { client, search, getSingleMedia, getRelatedMedia, stats }
}
