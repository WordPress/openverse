import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { isRetriable } from "~/utils/errors"

import { AUDIO, IMAGE } from "~/constants/media"

import type { Middleware } from "@nuxt/types"

const isSearchPath = (path: string) => path.includes("/search/")
const isCollectionPath = (path: string) => path.includes("/collection")

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

    if (!media) {
      const fetchingError = singleResultStore.fetchState.fetchingError

      if (fetchingError && !isRetriable(fetchingError)) {
        error(fetchingError ?? {})
      }
    }
    await useRelatedMediaStore($pinia).fetchMedia(mediaType, route.params.id)
  } else {
    // Client-side rendering
    singleResultStore.setMediaById(mediaType, route.params.id)

    console.log(
      from,
      from.path,
      isSearchPath(from.path),
      isCollectionPath(from.path)
    )
    if (from && (isSearchPath(from.path) || isCollectionPath(from.path))) {
      const searchStore = useSearchStore($pinia)
      searchStore.setBackToSearchPath(from.fullPath)

      if (isSearchPath(from.path)) {
        const searchTerm = Array.isArray(route.query.q)
          ? route.query.q[0]
          : route.query.q

        if (searchTerm) {
          searchStore.setSearchTerm(searchTerm)
        }
      }
    }
  }
}
