import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { skipToContentTargetId } from "~/constants/window"

import { handledClientSide } from "~/utils/errors"

import type { Middleware } from "@nuxt/types"

export const searchMiddleware: Middleware = async ({
  redirect,
  route,
  $pinia,
  error: nuxtError,
}) => {
  const {
    query: { q: rawQ },
  } = route
  const q = Array.isArray(rawQ) ? rawQ[0] : rawQ

  /**
   * This middleware redirects any search without a query to the homepage.
   * This is meant to block direct access to /search and all sub-routes.
   *
   * The `q` parameter is required for searches on the frontend.
   */
  if (!q) {
    return redirect("/")
  }

  // Don't do anything when clicking on the skip-to-content link.
  if (route.hash === `#${skipToContentTargetId}`) {
    return
  }

  const searchStore = useSearchStore($pinia)

  await searchStore.initProviderFilters()

  searchStore.setSearchStateFromUrl({
    path: route.path,
    urlQuery: route.query,
  })

  // Fetch results before rendering the page on the server.
  if (process.server) {
    const mediaStore = useMediaStore($pinia)
    const results = await mediaStore.fetchMedia()

    const fetchingError = mediaStore.fetchState.fetchingError
    if (!results.length && fetchingError && !handledClientSide(fetchingError)) {
      nuxtError(fetchingError)
    }
  }
}
