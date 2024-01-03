import { defineNuxtRouteMiddleware, showError } from "#imports"

import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { isRetriable } from "~/utils/errors"
import { firstParam } from "~/utils/query-utils"

import { AUDIO, IMAGE } from "~/constants/media"

const isSearchPath = (path: string) => path.includes("/search/")
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

    if (process.server) {
      const media = await singleResultStore.fetch(mediaType, mediaId)
      if (media) {
        await useRelatedMediaStore().fetchMedia(mediaType, mediaId)
      } else {
        const fetchingError = singleResultStore.fetchState.fetchingError

        if (fetchingError && !isRetriable(fetchingError)) {
          return showError(fetchingError)
        }
      }
    } else {
      // Client-side rendering
      singleResultStore.setMediaById(mediaType, mediaId)

      if (from && isSearchOrCollectionPath(from.path)) {
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
