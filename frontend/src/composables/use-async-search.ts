import {
  areQueriesEqual,
  handledClientSide,
  isClient,
  navigateTo,
  showError,
  useAsyncData,
  useFeatureFlagStore,
  useSearchStore,
} from "#imports"

import { computed, ref, watch } from "vue"
import { watchDebounced } from "@vueuse/core"
import { storeToRefs } from "pinia"

import { useMediaStore } from "~/stores/media"
import { INCLUDE_SENSITIVE_QUERY_PARAM } from "~/constants/content-safety"
import { SearchFilterKeys, SearchQuery } from "~/types/search"

const excludedKeys = new Set([INCLUDE_SENSITIVE_QUERY_PARAM, "q"])
/**
 * Extracts the filters from the search store API query object.
 * The `q` and `fetch_sensitive` params are excluded because they
 * are handled separately.
 */
const extractFiltersFromQuery = (query: SearchQuery) => {
  return (Object.keys(query) as SearchFilterKeys[])
    .filter((key) => !excludedKeys.has(key))
    .reduce((obj, key) => {
      obj[key] = query[key]
      return obj
    }, {} as SearchQuery)
}

export const useAsyncSearch = async () => {
  const featureFlagStore = useFeatureFlagStore()
  const mediaStore = useMediaStore()
  const searchStore = useSearchStore()

  const scrollToTop = () => {
    document.getElementById("main-page")?.scroll(0, 0)
  }

  const {
    searchTerm,
    searchType,
    apiSearchQueryParams: query,
  } = storeToRefs(searchStore)

  /**
   * This watcher fires whenever the search store API query object
   * changes: on search term, fetch_sensitive, search type or filters
   * change.
   * Here, we select only the changes in the filters, and debounce the
   * watcher to prevent sending too many requests.
   */
  const debouncedQuery = ref(extractFiltersFromQuery(query.value))
  watchDebounced(
    query,
    (newQuery, oldQuery) => {
      const newFilters = extractFiltersFromQuery(newQuery)
      if (!areQueriesEqual(newFilters, extractFiltersFromQuery(oldQuery))) {
        debouncedQuery.value = newFilters
        page.value = 1
        return navigateTo(searchStore.getSearchPath())
      }
    },
    { debounce: 800, maxWait: 5000 }
  )

  const shouldFetchSensitiveResults = computed(() =>
    featureFlagStore.isOn("fetch_sensitive")
  )
  watch(shouldFetchSensitiveResults, () => {
    page.value = 1
  })

  const page = ref(1)

  const { error } = await useAsyncData(
    "search",
    async () => {
      const isFirstPageRequest = page.value < 2

      if (isFirstPageRequest && isClient) {
        scrollToTop()
      }
      return await mediaStore.fetchMedia({
        shouldPersistMedia: !isFirstPageRequest,
      })
    },
    {
      watch: [
        shouldFetchSensitiveResults,
        searchTerm,
        searchType,
        page,
        debouncedQuery,
      ],
      immediate: true,
      lazy: isClient ?? false,
      /**
       * We need to return data from useAsyncData to prevent re-fetching on the server.
       * However, we use the data from the store in the components because it's updated
       * when we need. So, to minimize the data sent to the client by the server, we add
       * a simple transform to return only ids.
       */
      transform: (data) => {
        if (data) {
          return data.map((item) => item.id)
        }
      },
    }
  )

  const fetchingError = computed(() => mediaStore.fetchState.fetchingError)
  watch(
    error,
    () => {
      const storeError = mediaStore.fetchState.fetchingError
      if (storeError && !handledClientSide(storeError)) {
        return showError({ ...(storeError ?? {}), fatal: true })
      }
    },
    { immediate: true }
  )
  const handleLoadMore = () => {
    page.value = page.value + 1
  }
  return { handleLoadMore, fetchingError }
}
