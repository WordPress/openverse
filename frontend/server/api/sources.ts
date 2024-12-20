import { consola } from "consola"
import { useRuntimeConfig, defineCachedFunction } from "nitropack/runtime"
import { defineEventHandler, getProxyRequestHeaders, type H3Event } from "h3"

import {
  supportedMediaTypes,
  type SupportedMediaType,
} from "#shared/constants/media"
import { userAgentHeader } from "#shared/constants/user-agent.mjs"
import { mediaSlug } from "#shared/utils/query-utils"

const UPDATE_FREQUENCY_SECONDS = 60 * 60 // 1 hour

type Sources = {
  [K in SupportedMediaType]: MediaProvider[]
}

const getSources = defineCachedFunction(
  async (mediaType: SupportedMediaType, event: H3Event) => {
    const apiUrl = useRuntimeConfig(event).public.apiUrl

    consola.info(`Fetching ${mediaType} sources.`)

    return await $fetch<MediaProvider[]>(
      `${apiUrl}v1/${mediaSlug(mediaType)}/stats/`,
      {
        headers: {
          ...getProxyRequestHeaders(event),
          ...userAgentHeader,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    )
  },
  {
    maxAge: UPDATE_FREQUENCY_SECONDS,
    name: "sources",
    getKey: (mediaType) => mediaType,
  }
)

/**
 * The cached function uses stale-while-revalidate (SWR) to fetch sources for each media type only once per hour.
 */
export default defineEventHandler(async (event) => {
  const sources: Sources = { audio: [], image: [] }

  for (const mediaType of supportedMediaTypes) {
    sources[mediaType] = await getSources(mediaType, event)
  }

  return sources
})
