import { useSearchStore } from "~/stores/search"

import type { Middleware } from "@nuxt/types"

export const singleResultMiddleware: Middleware = ({ route, from, $pinia }) => {
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
