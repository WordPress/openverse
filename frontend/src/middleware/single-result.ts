import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"

import { AUDIO, IMAGE } from "~/constants/media"

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
    const media = await singleResultStore.fetch(mediaType, route.params.id)
    await useRelatedMediaStore($pinia).fetchMedia(mediaType, route.params.id)

    if (!media) {
      error(singleResultStore.fetchState.fetchingError ?? {})
    }
  } else {
    // Client-side rendering
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
