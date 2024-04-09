import { decodeMediaData } from "~/utils/decode-media-data"
import type {
  PaginatedCollectionQuery,
  PaginatedSearchQuery,
} from "~/types/search"
import type { ApiService } from "~/data/api-service"
import type { DetailFromMediaType, Media } from "~/types/media"
import { AUDIO, type SupportedMediaType } from "~/constants/media"
import type { Events } from "~/types/analytics"

import type { AxiosResponse } from "axios"

export type SearchTimeEventPayload = Events["SEARCH_RESPONSE_TIME"]

export interface MediaResult<
  T extends Media | Media[] | Record<string, Media>,
> {
  result_count: number
  page_count: number
  page_size: number
  page: number
  results: T
}

class MediaService<T extends Media> {
  private readonly apiService: ApiService
  private readonly mediaType: T["frontendMediaType"]

  constructor(apiService: ApiService, mediaType: T["frontendMediaType"]) {
    this.apiService = apiService
    this.mediaType = mediaType
  }

  /**
   * Processes AxiosResponse from a search query to construct
   * SEARCH_RESPONSE_TIME analytics event payload.
   * @param response - Axios response
   * @param requestDatetime - datetime before request was sent
   */
  buildEventPayload(
    response: AxiosResponse,
    requestDatetime: Date
  ): SearchTimeEventPayload | undefined {
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
      cfCacheStatus: String(responseHeaders["cf-cache-status"]),
      cfRayIATA: String(cfRayIATA),
      elapsedTime: elapsedSeconds,
      queryString: url.search,
      mediaType: this.mediaType,
    }
  }

  /**
   * Decodes the text data to avoid encoding problems.
   * Also, converts the results from an array of media
   * objects into an object with media id as keys.
   * @param data - search result data
   */
  transformResults(data: MediaResult<T[]>): MediaResult<Record<string, T>> {
    const mediaResults = <T[]>data.results ?? []
    return {
      ...data,
      results: mediaResults.reduce(
        (acc, item) => {
          acc[item.id] = decodeMediaData(item, this.mediaType)
          return acc
        },
        {} as Record<string, T>
      ),
    }
  }

  /**
   * Search for media items by keyword.
   * @param params - API search query parameters
   */
  async search(
    params: PaginatedSearchQuery | PaginatedCollectionQuery
  ): Promise<{
    eventPayload: SearchTimeEventPayload | undefined
    data: MediaResult<Record<string, Media>>
  }> {
    // Add the `peaks` param to all audio searches automatically
    if (this.mediaType === AUDIO) {
      params.peaks = "true"
    }

    const requestDatetime = new Date()

    const res = await this.apiService.query<MediaResult<T[]>>(
      this.mediaType,
      params as unknown as Record<string, string>
    )

    const eventPayload = this.buildEventPayload(res, requestDatetime)

    return { eventPayload, data: this.transformResults(res.data) }
  }

  /**
   * Retrieve media details by its id.
   * SSR-called
   * @param id - the media id to fetch
   */
  async getMediaDetail(id: string): Promise<T> {
    if (!id) {
      throw new Error(
        `MediaService.getMediaDetail() id parameter required to retrieve ${this.mediaType} details.`
      )
    }
    const res = await this.apiService.get<T>(this.mediaType, id)
    return decodeMediaData(res.data, this.mediaType)
  }

  /**
   * Retrieve related media.
   * @param id - object with id of the main media, for which to fetch related media
   */
  async getRelatedMedia<T extends SupportedMediaType>(
    id: string
  ): Promise<MediaResult<DetailFromMediaType<T>[]>> {
    if (!id) {
      throw new Error(
        `MediaService.getRelatedMedia() id parameter required to retrieve related media.`
      )
    }
    const params = this.mediaType === AUDIO ? { peaks: "true" } : undefined
    const res = (await this.apiService.get(
      this.mediaType,
      `${id}/related`,
      params
    )) as AxiosResponse<MediaResult<DetailFromMediaType<T>[]>>
    return {
      ...res.data,
      results: (res.data.results ?? []).map((item) =>
        decodeMediaData(item, this.mediaType)
      ) as DetailFromMediaType<T>[],
    }
  }
}

export default MediaService
