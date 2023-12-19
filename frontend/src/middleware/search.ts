import { navigateTo, defineNuxtRouteMiddleware, firstParam } from "#imports"

import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"

import { handledClientSide } from "~/utils/errors"

export const searchMiddleware = defineNuxtRouteMiddleware(async (to) => {
  const {
    query: { q: rawQ },
  } = to
  const q = firstParam(rawQ)
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

  // Fetch results before rendering the page on the server.
  if (process.server) {
    const searchStore = useSearchStore()

    await searchStore.initProviderFilters()
    searchStore.setSearchStateFromUrl({
      path: to.path,
      urlQuery: to.query,
    })
    const mediaStore = useMediaStore()

    const results = await mediaStore.fetchMedia()
    const fetchingError = mediaStore.fetchState.fetchingError
    if (!results && fetchingError && !handledClientSide(fetchingError)) {
      // TODO: handle error
      console.log("Error: ", fetchingError)
    }
  }
})
