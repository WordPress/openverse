import { AUDIO, type SupportedMediaType } from "#shared/constants/media"
import { INTERNAL_REQUEST_HEADER } from "#shared/constants/proxy"
import type { Media } from "#shared/types/media"
import type {
  PaginatedCollectionQuery,
  PaginatedSearchQuery,
} from "#shared/types/search"
import {
  type MediaResult,
  type SearchTimeEventPayload,
  transformResults,
} from "~/data/api-service"
import { decodeMediaData } from "~/utils/decode-media-data"
import type { useProviderStore } from "~/stores/provider"

type RequestFetch = typeof $fetch

export interface ProxyServiceConfig {
  requestFetch: RequestFetch
  providerStore: ReturnType<typeof useProviderStore>
  /** whether to use fake sensitivity data for testing */
  fakeSensitive?: boolean
  /**
   * The token that marks the in-process SSR requests, so that the rate limits
   * don't count them twice. Only set on the server.
   */
  internalRequestToken?: string
}

/**
 * Creates a client with the same interface as `createApiClient` that sends
 * the requests to the Nuxt server routes instead of the API. The server
 * routes add the frontend's API credentials.
 *
 * It must not call composables, because it is called inside store actions.
 */
export const createProxyClient = ({
  requestFetch,
  providerStore,
  fakeSensitive = false,
  internalRequestToken,
}: ProxyServiceConfig) => {
  const headers: Record<string, string> = internalRequestToken
    ? { [INTERNAL_REQUEST_HEADER]: internalRequestToken }
    : {}

  const search = async <T extends Media>(
    mediaType: SupportedMediaType,
    query: PaginatedSearchQuery | PaginatedCollectionQuery
  ) => {
    // Add the `peaks` param to all audio searches automatically
    if (mediaType === AUDIO) {
      query.peaks = "true"
    }
    const { eventPayload, data } = await requestFetch<{
      eventPayload?: SearchTimeEventPayload
      data: MediaResult<T[]>
    }>(`/api/search/${mediaType}/`, { query, headers })

    return {
      eventPayload,
      data: transformResults(mediaType, data, fakeSensitive, providerStore),
    }
  }

  const getSingleMedia = async <T extends Media>(
    mediaType: SupportedMediaType,
    id: string
  ) => {
    const data = await requestFetch<T>(`/api/${mediaType}/${id}/`, { headers })
    return decodeMediaData(data, mediaType, false, providerStore)
  }

  const getRelatedMedia = async (mediaType: SupportedMediaType, id: string) => {
    const query = mediaType === AUDIO ? { peaks: "true" } : {}
    const data = await requestFetch<{ results: Media[] }>(
      `/api/${mediaType}/related/${id}/`,
      { query, headers }
    )
    return data.results.map((media) =>
      decodeMediaData(media, mediaType, false, providerStore)
    )
  }

  return { search, getSingleMedia, getRelatedMedia }
}
