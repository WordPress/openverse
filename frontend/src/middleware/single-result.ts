import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"

import { AUDIO, IMAGE } from "~/constants/media"

import type { Middleware } from "@nuxt/types"

export const singleResultMiddleware: Middleware = async ({
  route,
  from,
  error,
  $pinia,
  $sentry,
}) => {
  const mediaType = route.fullPath.includes("/image/") ? IMAGE : AUDIO
  const singleResultStore = useSingleResultStore($pinia)
  if (process.server) {
    try {
      await singleResultStore.fetch(mediaType, route.params.id)
    } catch (e) {
      // Capture the error in Sentry and show error page.
      // TODO: Use different error page for 429 and 500.
      $sentry.captureException(e)
      error(singleResultStore.fetchState.fetchingError ?? {})
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
