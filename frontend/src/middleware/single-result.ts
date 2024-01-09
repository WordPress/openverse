import { defineNuxtRouteMiddleware } from "#imports"

import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE } from "~/constants/media"

import { firstParam } from "~/utils/query-utils"

const isSearchPath = (fullPath: string) => {
  return fullPath.includes("/search/") || fullPath.includes("/search?")
}
const isSearchOrCollectionPath = (path: string) =>
  isSearchPath(path) || path.includes("/source/") || path.includes("/tag/")

export const singleResultMiddleware = defineNuxtRouteMiddleware(
  async (to, from) => {
    const mediaType = to.fullPath.includes("/image/") ? IMAGE : AUDIO
    const mediaId = firstParam(to.params.id)
    if (!mediaId) {
      return
    }

    const singleResultStore = useSingleResultStore()

    if (process.client) {
      singleResultStore.setMediaById(mediaType, mediaId)

      if (from && isSearchOrCollectionPath(from.fullPath)) {
        const searchStore = useSearchStore()
        searchStore.setBackToSearchPath(from.fullPath)

        if (isSearchPath(from.path)) {
          const searchTerm = firstParam(to.query.q)

          if (searchTerm) {
            searchStore.setSearchTerm(searchTerm)
          }
        }
      }
    }
  }
)
