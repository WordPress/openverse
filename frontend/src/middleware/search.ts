import {
  navigateTo,
  defineNuxtRouteMiddleware,
  firstParam,
  handledClientSide,
  createError,
  useNuxtApp,
  showError,
} from "#imports"

import { useMediaStore } from "~/stores/media"
import { skipToContentTargetId } from "~/constants/window"

import { useSearchStore } from "~/stores/search"

export const searchMiddleware = defineNuxtRouteMiddleware(async (to) => {
  const {
    query: { q },
  } = to
  /**
   * This middleware redirects any search without a query to the homepage.
   * This is meant to block direct access to /search and all sub-routes.
   *
   * The `q` parameter is required for searches on the frontend.
   */
  if (!firstParam(q)) {
    return navigateTo("/")
  }

  // Don't do anything when clicking on the skip-to-content link.
  if (to.hash === `#${skipToContentTargetId}`) {
    return
  }

  const searchStore = useSearchStore()

  await searchStore.initProviderFilters()

  const nuxtApp = useNuxtApp()
  // Set the state from url on the first server rendering, and on client navigation
  if (!nuxtApp.isHydrating) {
    searchStore.setSearchStateFromUrl({
      path: to.path,
      urlQuery: to.query,
    })
  }

  // Fetch results before rendering the page on the server.
  if (import.meta.server) {
    const mediaStore = useMediaStore()
    const results = await mediaStore.fetchMedia()

    const fetchingError = mediaStore.fetchState.fetchingError
    if (!results.length && fetchingError && !handledClientSide(fetchingError)) {
      showError(createError(fetchingError))
    }
  }
})
