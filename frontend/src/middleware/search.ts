import { navigateTo, defineNuxtRouteMiddleware, showError } from "#imports"

import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { handledClientSide } from "~/utils/errors"

export const searchMiddleware = defineNuxtRouteMiddleware(async (to) => {
  const {
    query: { q: rawQ },
  } = to
  const q = Array.isArray(rawQ) ? rawQ[0] : rawQ
  /**
   * This middleware redirects any search without a query to the homepage.
   * This is meant to block direct access to /search and all sub-routes.
   *
   * The `q` parameter is required for searches on the frontend.
   * The API also allows for calls without the `q` parameter when searching within
   * `creator` field, but the frontend query still uses `q` for it.
   * The `?q=cat&searchBy=creator` frontend query is converted to
   * `?creator=cat&searchBy=creator` API request query in
   * `prepare-search-query-params`.
   * Note that the search by creator is not displayed in the UI.
   */
  if (!q) {
    return navigateTo("/")
  }

  const searchStore = useSearchStore()

  searchStore.setSearchStateFromUrl({
    path: to.path,
    urlQuery: to.query,
  })

  // Fetch results before rendering the page on the server.
  if (process.server) {
    await searchStore.initProviderFilters()

    const mediaStore = useMediaStore()

    const results = await mediaStore.fetchMedia()
    const fetchingError = mediaStore.fetchState.fetchingError
    if (!results && fetchingError && !handledClientSide(fetchingError)) {
      return showError(fetchingError)
    }
  }
})
