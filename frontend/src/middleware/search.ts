import { useSearchStore } from "~/stores/search"

import type { Middleware } from "@nuxt/types"

export const searchMiddleware: Middleware = ({ redirect, route, $pinia }) => {
  const {
    query: { q, searchBy },
  } = route
  /**
   * This anonymous middleware redirects any search without a query to the homepage.
   * This is meant to block direct access to /search and all sub-routes, with
   * an exception for the 'creator' filter. The creator filter doesn't send
   * the search query to the API.
   */
  if (!q && !searchBy) return redirect("/")
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
