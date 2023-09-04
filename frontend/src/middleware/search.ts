import { useSearchStore } from "~/stores/search"
import { useMediaStore } from "~/stores/media"
import { NO_RESULT } from "~/constants/errors"

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
   * The API also allows for calls without the `q` parameter when searching within
   * `creator` field, but the frontend query still uses `q` for it.
   * The `?q=cat&searchBy=creator` frontend query is converted to
   * `?creator=cat&searchBy=creator` API request query in
   * `prepare-search-query-params`.
   * Note that the search by creator is not displayed in the UI.
   */
  if (!q) return redirect("/")

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
    // NO_RESULTS and timeout are handled client-side, for other errors show server error page
    if (
      !results &&
      fetchingError &&
      !fetchingError?.message?.includes(NO_RESULT) &&
      !fetchingError?.message?.includes("timeout")
    ) {
      nuxtError(fetchingError)
    }
  }
}
