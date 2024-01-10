import { navigateTo, defineNuxtRouteMiddleware, firstParam } from "#imports"

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
   * The API also allows for calls without the `q` parameter when searching within
   * `creator` field, but the frontend query still uses `q` for it.
   * The `?q=cat&searchBy=creator` frontend query is converted to
   * `?creator=cat&searchBy=creator` API request query in
   * `prepare-search-query-params`.
   * Note that the search by creator is not displayed in the UI.
   */
  if (!firstParam(q)) {
    return navigateTo("/")
  }

  const searchStore = useSearchStore()

  searchStore.setSearchStateFromUrl({
    path: to.path,
    urlQuery: to.query,
  })
  await searchStore.initProviderFilters()
})
