import { AxiosResponse } from "axios"

import type { SupportedMediaType } from "#shared/constants/media"
import { SearchTimeEventPayload } from "~/data/api-service"

const getElapsedTime = (
  requestDatetime: Date,
  dateHeader: string | undefined
): number | null => {
  if (!dateHeader) {
    return null
  }
  const responseDatetime = new Date(dateHeader)
  if (responseDatetime < requestDatetime) {
    // response returned was from the local cache
    return null
  }
  return Math.floor(
    (responseDatetime.getTime() - requestDatetime.getTime()) / 1000
  )
}
const getCfRayIATA = (cfRayHeader: unknown): string | null => {
  if (
    !cfRayHeader ||
    typeof cfRayHeader !== "string" ||
    !cfRayHeader.includes("-")
  ) {
    return null
  }

  return cfRayHeader.split("-")[1]
}
export const getQueryString = (
  request: AxiosResponse["request"]
): string | null => {
  const responseUrl = request?.responseURL ?? request?.res?.responseUrl
  if (!responseUrl) {
    return null
  }
  const url = new URL(responseUrl)
  return url.search
}
/**
 * Processes AxiosResponse from a search query to construct
 * SEARCH_RESPONSE_TIME analytics event payload.
 * @param responseHeaders - the headers to extract cache and timing information from
 * @param queryString - the search query string
 * @param requestDatetime - datetime before request was sent
 * @param mediaType - the media type of the search query
 */
export const buildEventPayload = (
  responseHeaders: AxiosResponse["headers"] | { [p: string]: string },
  queryString: string,
  requestDatetime: Date,
  mediaType: SupportedMediaType
): SearchTimeEventPayload | undefined => {
  const REQUIRED_HEADERS = ["date", "cf-cache-status", "cf-ray"]

  if (!REQUIRED_HEADERS.every((header) => header in responseHeaders)) {
    // console.debug("Missing required headers")
    return
  }

  const cfRayIATA = getCfRayIATA(responseHeaders["cf-ray"])
  if (!cfRayIATA) {
    // console.debug("Invalid cf-ray header")
    return
  }

  const elapsedTime = getElapsedTime(requestDatetime, responseHeaders["date"])
  if (elapsedTime === null) {
    // console.debug("Response was from cache")
    return
  }

  return {
    cfCacheStatus: responseHeaders["cf-cache-status"].toString(),
    cfRayIATA,
    elapsedTime,
    queryString,
    mediaType,
  }
}
