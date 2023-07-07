import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE } from "~/constants/media"

import type { Middleware } from "@nuxt/types"

export const singleResultMiddleware: Middleware = ({ route, from, $pinia }) => {
  const mediaType = route.fullPath.includes("/image/") ? IMAGE : AUDIO
  useSingleResultStore($pinia).setMediaById(mediaType, route.params.id)

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
