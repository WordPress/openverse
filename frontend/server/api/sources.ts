import { ofetch } from "ofetch"
import { consola } from "consola"
import { defineEventHandler } from "h3"
import { useRuntimeConfig } from "nitropack/runtime"
import { useStorage } from "nitropack/runtime/storage"

import { supportedMediaTypes } from "#shared/constants/media"
import type { SupportedMediaType } from "#shared/constants/media"
import { mediaSlug } from "#shared/utils/query-utils"

const UPDATE_FREQUENCY = 1000 * 60 * 60 // 1 hour

const needsUpdate = (lastUpdated: Date | null | undefined) => {
  if (!lastUpdated) {
    return true
  }
  const timePassed = new Date().getTime() - new Date(lastUpdated).getTime()
  return timePassed > UPDATE_FREQUENCY
}

type MediaTypeCache = { data: MediaProvider[]; updatedAt: Date | null }

type Sources = {
  [K in SupportedMediaType]: MediaProvider[]
}

const SOURCES = "sources"

/**
 * This endpoint that returns cached sources data for all supported media types,
 * if the data is no older than `UPDATE_FREQUENCY`.
 * Otherwise, it fetches the data from the API, caches it and returns the updated data.
 */
export default defineEventHandler(async (event) => {
  const cache = useStorage<MediaTypeCache>(SOURCES)

  const sources = { image: [], audio: [] } as Sources

  for (const mediaType of supportedMediaTypes) {
    const cacheKey = `${SOURCES}:${mediaType}`

    const cachedSources = await cache.getItem(cacheKey)
    const expired = needsUpdate(cachedSources?.updatedAt)

    if (cachedSources && cachedSources.data?.length && !expired) {
      sources[mediaType] = cachedSources.data
      consola.debug(`Using cached ${mediaType} sources data.`)
    } else {
      const reason = !cachedSources
        ? "cache is not set"
        : !cachedSources.data?.length
          ? "the cached array is empty"
          : "cache is outdated"

      consola.debug(`Fetching ${mediaType} sources data because ${reason}.`)
      const apiUrl = useRuntimeConfig(event).public.apiUrl
      try {
        const res = await ofetch<MediaProvider[]>(
          `${apiUrl}v1/${mediaSlug(mediaType)}/stats`,
          { headers: event.headers }
        )
        const updatedAt = new Date()
        await cache.setItem(cacheKey, { data: res, updatedAt })
        consola.info(
          `Fetched ${res.length} ${mediaType} sources data on ${updatedAt.toISOString()}.`
        )
        sources[mediaType] = res
      } catch (error) {
        consola.error("Error fetching sources data", error)
        event.context.$sentry.captureException(error)
        sources[mediaType] = cachedSources?.data ?? []
      }
    }
  }

  return sources
})
