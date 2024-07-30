import {
  createError,
  defineNuxtRouteMiddleware,
  firstParam,
  handledClientSide,
  showError,
} from "#imports"

import { RouteLocationNormalized } from "vue-router"

import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { getRouteNameString } from "~/utils/route-utils"

const searchPaths = [
  ...supportedMediaTypes.map((type) => `search-${type}`),
  "search",
]

const isSearchPath = (route: RouteLocationNormalized) => {
  return searchPaths.includes(getRouteNameString(route).split("__")[0])
}
const isCollectionPath = (path: string) => path.includes("/collection")

export default defineNuxtRouteMiddleware(async (to, from) => {
  const mediaType = to.fullPath.includes("/image/") ? IMAGE : AUDIO
  const singleResultStore = useSingleResultStore()
  const relatedMediaStore = useRelatedMediaStore()

  const mediaId = firstParam(to?.params.id)
  if (!mediaId) {
    return
  }
  singleResultStore.setMediaById(mediaType, mediaId)
  if (import.meta.server) {
    await Promise.allSettled([
      singleResultStore.fetch(mediaType, mediaId),
      relatedMediaStore.fetchMedia(mediaType, mediaId),
    ])

    const fetchingError = singleResultStore.fetchState.fetchingError
    if (
      !singleResultStore.mediaItem &&
      fetchingError &&
      !handledClientSide(fetchingError)
    ) {
      showError(createError(fetchingError))
    }
  } else if (from && (isSearchPath(from) || isCollectionPath(from.path))) {
    const searchStore = useSearchStore()
    searchStore.setBackToSearchPath(from.fullPath)

    if (isSearchPath(from)) {
      const searchTerm = firstParam(to?.query.q) ?? ""
      if (searchTerm) {
        searchStore.setSearchTerm(searchTerm)
      }
    }
  }
})
