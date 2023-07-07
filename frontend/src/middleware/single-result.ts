import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE } from "~/constants/media"

import { warn } from "~/utils/console"

import type { Middleware } from "@nuxt/types"

export const singleResultMiddleware: Middleware = async ({
  route,
  from,
  error,
  $pinia,
}) => {
  const mediaType = route.fullPath.includes("/image/") ? IMAGE : AUDIO
  const singleResultStore = useSingleResultStore($pinia)
  if (process.server) {
    try {
      await singleResultStore.fetch(mediaType, route.params.id)
      if (!singleResultStore.mediaItem) {
        error({ statusCode: 404 })
      }
    } catch (e) {
      warn(`Could not fetch ${mediaType} with id ${route.params.id}`)
      error({ statusCode: 404 })
    }
  } else {
    singleResultStore.setMediaById(mediaType, route.params.id)
    if (from && from.path.includes("/search/")) {
      const searchStore = useSearchStore($pinia)
      searchStore.setBackToSearchPath(from.fullPath)
      const searchTerm = Array.isArray(route.query.q)
        ? route.query.q[0]
        : route.query.q
      if (searchTerm) {
        searchStore.setSearchTerm(searchTerm)
      }
    }
  }
}
