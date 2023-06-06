import { useSearchStore } from "~/stores/search"

import type { Middleware } from "@nuxt/types"

export const searchMiddleware: Middleware = ({ redirect, route, $pinia }) => {
  const {
    query: { q },
  } = route
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
  if (!q) return redirect("/")
  /**
   * We need to make sure that query `q` exists before checking if it matches
   * the store searchTerm.
   */
  const searchStore = useSearchStore($pinia)
  const querySearchTerm = Array.isArray(q) ? q[0] : q
  if (querySearchTerm !== searchStore.searchTerm) {
    searchStore.setSearchTerm(querySearchTerm)
  }
}
