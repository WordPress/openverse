import { defineNuxtRouteMiddleware } from "#imports"

import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE } from "~/constants/media"

import { firstParam, validateUUID } from "~/utils/query-utils"
import { useSingleResultStore } from "~/stores/media/single-result"

const isSearchPath = (fullPath: string) => {
  return fullPath.includes("/search/") || fullPath.includes("/search?")
}
const isSearchOrCollectionPath = (path: string) =>
  isSearchPath(path) || path.includes("/source/") || path.includes("/tag/")

export const singleResultMiddleware = defineNuxtRouteMiddleware(
  async (to, from) => {
    const mediaId = firstParam(to.params.id)
    if (!mediaId || !validateUUID(mediaId)) {
      return
    }

    const singleResultStore = useSingleResultStore()
    const mediaType = to.fullPath.includes("/image/") ? IMAGE : AUDIO
    singleResultStore.setMediaById(mediaType, mediaId)

    if (process.client) {
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
