import { defineStore } from "pinia"

import { useStorage } from "@vueuse/core"

import { env } from "~/utils/env"
import { deepClone } from "~/utils/clone"
import type { DeepWriteable } from "~/types/utils"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  SearchType,
  SupportedMediaType,
  supportedMediaTypes,
  SupportedSearchType,
  supportedSearchTypes,
  isAdditionalSearchType,
  searchPath,
} from "~/constants/media"
import {
  filtersToQueryData,
  queryDictionaryToQueryParams,
  pathToSearchType,
  queryToFilterData,
} from "~/utils/search-query-transform"
import {
  FilterCategory,
  FilterItem,
  Filters,
  filterData,
  mediaFilterKeys,
  mediaUniqueFilterKeys,
} from "~/constants/filters"
import { INCLUDE_SENSITIVE_QUERY_PARAM } from "~/constants/content-safety"

import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"

import type {
  SearchQuery,
  SearchStrategy,
  PaginatedSearchQuery,
  CollectionParams,
  PaginatedCollectionQuery,
} from "~/types/search"

import type { Ref } from "vue"
import type { Dictionary } from "vue-router/types/router"
import type { Context } from "@nuxt/types"

export const isSearchTypeSupported = (
  st: SearchType
): st is SupportedSearchType => {
  return supportedSearchTypes.includes(st as SupportedSearchType)
}

export interface SearchState {
  searchType: SearchType
  strategy: SearchStrategy
  collectionParams: CollectionParams | null
  recentSearches: Ref<string[]>
  backToSearchPath: string
  searchTerm: string
  localSearchTerm: string
  filters: Filters
}

export function getSensitiveQuery(
  mode: "frontend" | "API"
): { unstable__include_sensitive_results: "true" } | Record<string, never> {
  if (mode === "frontend") {
    return {}
  }
  // `INCLUDE_SENSITIVE_QUERY_PARAM` is used in the API params, but not shown on the frontend.
  const ffStore = useFeatureFlagStore()
  return ffStore.isOn("fetch_sensitive")
    ? { [INCLUDE_SENSITIVE_QUERY_PARAM]: "true" }
    : {}
}

/**
 * Builds the search query parameters for the given search type, filters, and search term.
 * `q` parameter is always included as the first query parameter.
 * If the search type is not supported, only the `q` parameter is included.
 * This is used, for instance, for content switcher links for `video`/`model_3d` search pages.
 * Only the filters that are relevant for the search type and have a value are included.
 *
 * `mode` parameter determines whether to add the `INCLUDE_SENSITIVE_QUERY_PARAM`
 * or not: frontend never shows this parameter, but it is added to the API query if the
 * feature flag is `on`.
 */
export function computeQueryParams(
  searchType: SearchType,
  filters: Filters,
  searchTerm: string,
  mode: "frontend" | "API"
) {
  const q = searchTerm.trim()
  if (!isSearchTypeSupported(searchType)) {
    return { q }
  }
  // Ensure that `q` always comes first in the frontend URL.
  const searchQuery: SearchQuery = {
    q,
    // The filters object is converted to a Record<string, string> object.
    // e.g., { licenseTypes: [{ code: "commercial", checked: true }] }
    // => { license_type: "commercial" }
    ...filtersToQueryData(filters, searchType),
    ...getSensitiveQuery(mode),
  }

  return searchQuery
}

// TODO: Remove `unstable__` parameters after https://github.com/WordPress/openverse/issues/3919
export function buildCollectionQuery(
  collectionParams: CollectionParams
): PaginatedCollectionQuery {
  const { collection, ...params } = collectionParams

  const query: PaginatedCollectionQuery = {
    ...params,
    ...getSensitiveQuery("API"),
    unstable__collection: collection,
    collection,
  }
  if ("tag" in query) {
    query.unstable__tag = query.tag
  }
  return query
}

export const useSearchStore = defineStore("search", {
  state: (): SearchState => ({
    searchType: ALL_MEDIA,
    searchTerm: "",
    strategy: "default",
    collectionParams: null,
    backToSearchPath: "",
    localSearchTerm: "",
    recentSearches: useStorage<string[]>("recent-searches", []),
    filters: deepClone(filterData as DeepWriteable<typeof filterData>),
  }),
  hydrate(state) {
    // @ts-expect-error https://github.com/microsoft/TypeScript/issues/43826
    state.recentSearches = useStorage<string[]>("recent-searches", [])
  },
  getters: {
    filterCategories(state) {
      return Object.keys(state.filters) as FilterCategory[]
    },

    /**
     * Returns the search query parameters for API request.
     * The main difference between api and frontend query parameters is that
     * the API query parameters include the `include_sensitive_results` parameter.
     */
    apiSearchQueryParams(state) {
      return computeQueryParams(
        state.searchType,
        state.filters,
        state.searchTerm,
        "API"
      )
    },

    /**
     * Returns the number of checked filters.
     */
    appliedFilterCount(state) {
      const filterKeys = mediaFilterKeys[state.searchType]
      return filterKeys.reduce((count, filterCategory) => {
        return (
          count + state.filters[filterCategory].filter((f) => f.checked).length
        )
      }, 0)
    },

    /**
     * Returns the object with filters for selected search type,
     * with codes, names for i18n labels, and checked status.
     */
    searchFilters(state) {
      return mediaFilterKeys[state.searchType].reduce((obj, filterKey) => {
        obj[filterKey] = this.filters[filterKey]
        return obj
      }, {} as Filters)
    },

    /**
     * True if any filter for selected search type is checked.
     */
    isAnyFilterApplied() {
      const filterEntries = Object.entries(this.searchFilters) as [
        string,
        FilterItem[],
      ][]
      return filterEntries.some(([, filterItems]) =>
        filterItems.some((filter) => filter.checked)
      )
    },
    /**
     * Returns whether the current `searchType` is a supported media type for search.
     */
    searchTypeIsSupported(state) {
      return isSearchTypeSupported(state.searchType)
    },
    /**
     * Returns the unique string representation of the current collection
     * when making collection searches.
     */
    collectionValue(): null | string {
      if (this.collectionParams === null) {
        return null
      }

      switch (this.collectionParams.collection) {
        case "creator": {
          return `${this.collectionParams.source}/${this.collectionParams.creator}`
        }
        case "source": {
          return this.collectionParams.source
        }
        case "tag": {
          return this.collectionParams.tag
        }
      }
    },
  },
  actions: {
    getApiRequestQuery(mediaType: SupportedMediaType) {
      const query: PaginatedSearchQuery | PaginatedCollectionQuery =
        this.collectionParams === null
          ? computeQueryParams(mediaType, this.filters, this.searchTerm, "API")
          : buildCollectionQuery(this.collectionParams)
      return query
    },
    setBackToSearchPath(path: string) {
      this.backToSearchPath = path
    },
    /**
     * Updates the search type and search term, and returns the
     * updated localized search path.
     */
    updateSearchPath({
      type,
      searchTerm,
    }: { type?: SearchType; searchTerm?: string } = {}): string {
      if (type) {
        this.setSearchType(type)
      }
      if (searchTerm) {
        this.setSearchTerm(searchTerm)
      }

      return this.getSearchPath()
    },
    /**
     * Returns localized frontend search path for the given search type.
     *
     * If search type is not provided, returns the path for the current search type.
     * If query is not provided, returns current query parameters.
     * If only the search type is provided, the query is computed for this search type.
     */
    getSearchPath({
      type,
      query,
    }: { type?: SearchType; query?: PaginatedSearchQuery } = {}): string {
      const searchType = type ?? this.searchType
      const queryParams =
        query ??
        computeQueryParams(
          searchType,
          this.filters,
          this.searchTerm,
          "frontend"
        )

      return this.$nuxt.localePath({
        path: searchPath(searchType),
        query: queryParams as unknown as Dictionary<string>,
      })
    },

    /**
     * Returns localized frontend path for the given collection.
     * Used for the tags, source and creator links throughout the app.
     */
    getCollectionPath({
      type,
      collectionParams,
    }: {
      type: SupportedMediaType
      collectionParams: CollectionParams
    }) {
      const path = `/${type}/collection`
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { collection: _, ...query } = collectionParams
      return this.$nuxt.localePath({ path, query })
    },

    setSearchType(type: SearchType) {
      const featureFlagStore = useFeatureFlagStore()
      if (
        !featureFlagStore.isOn("additional_search_types") &&
        isAdditionalSearchType(type)
      ) {
        throw new Error(
          `Please enable the 'additional_search_types' flag to use the ${type}`
        )
      }

      this.searchType = type
      this.clearOtherMediaTypeFilters(type)
    },
    /**
     * The user can set several `q` query parameters, but we only
     * use the first one.
     * @param q - The URL `q` query parameter
     */
    setSearchTerm(q: string | undefined | null) {
      const formattedTerm = q ? q.trim() : ""
      if (this.searchTerm === formattedTerm) {
        return
      }
      this.searchTerm = formattedTerm
      this.localSearchTerm = formattedTerm
      this.collectionParams = null
      this.strategy = "default"

      this.addRecentSearch(formattedTerm)
    },
    /**
     * Sets the collectionParams and mediaType for the collection page.
     * Resets the filters and search term.
     */
    setCollectionState(
      collectionParams: CollectionParams,
      mediaType: SupportedMediaType
    ) {
      this.collectionParams = collectionParams
      this.strategy = collectionParams.collection
      this.setSearchType(mediaType)
      this.clearFilters()
    },
    /**
     * Called before navigating to a `/search` path, and when the
     * path after `/search` or query parameters change.
     */
    setSearchStateFromUrl({
      path,
      urlQuery,
    }: {
      path: string
      urlQuery: Context["query"]
    }) {
      const query = queryDictionaryToQueryParams(urlQuery)

      this.strategy = "default"
      this.collectionParams = null

      const mediaStore = useMediaStore()
      mediaStore.clearMedia()

      this.setSearchTerm(query.q)
      this.searchType = pathToSearchType(path)

      if (!isSearchTypeSupported(this.searchType)) {
        return
      }

      const newFilterData = queryToFilterData({
        query,
        searchType: this.searchType,
        defaultFilters: this.getBaseFiltersWithProviders(),
      })
      this.replaceFilters(newFilterData)
    },
    /**
     * This method need not exist and is only used to fix an odd
     * hydration bug in the search route. After navigating from
     * the homepage, the watcher in useStorage doesn't work.
     */
    refreshRecentSearches() {
      // @ts-expect-error https://github.com/microsoft/TypeScript/issues/43826
      this.recentSearches = useStorage<string[]>("recent-searches", [])
    },
    /** Add a new term to the list of recent search terms */
    addRecentSearch(
      search: string /** A search term to add to the saved list.*/
    ) {
      /**
       * Add the latest search to the top of the stack,
       * then add the existing items, making sure not to exceed
       * the max count, and removing existing occurrences of the
       * latest search term, if there are any.
       */
      this.recentSearches = [
        search,
        ...this.recentSearches.filter((i) => i !== search),
      ].slice(0, parseInt(env.savedSearchCount))
    },
    clearRecentSearches() {
      this.recentSearches = []
    },
    clearRecentSearch(idx: number) {
      this.recentSearches.splice(idx, 1)
    },
    /**
     * Initial filters do not include the provider filters. We create the provider filters object
     * when we fetch the provider data on the Nuxt server initialization.
     * We call this function to reset the filters to the initial base filters AND the provider filters.
     */
    getBaseFiltersWithProviders() {
      const resetProviders = (mediaType: SupportedMediaType): FilterItem[] => {
        return this.filters[`${mediaType}Providers`].map((provider) => ({
          ...provider,
          checked: false,
        }))
      }
      return {
        ...(deepClone(filterData) as DeepWriteable<typeof filterData>),
        audioProviders: resetProviders(AUDIO),
        imageProviders: resetProviders(IMAGE),
      }
    },

    async initProviderFilters() {
      const providerStore = useProviderStore()
      const providers = await providerStore.getProviders()

      for (const mediaType of supportedMediaTypes) {
        this.updateProviderFilters({
          mediaType,
          providers: providers[mediaType],
        })
      }
    },
    /**
     * Merge providers from API response with the filters that came from the browse URL search query string
     * and match the checked properties in the store.
     */
    updateProviderFilters({
      mediaType,
      providers,
    }: {
      mediaType: SupportedMediaType
      providers: { source_name: string; display_name: string }[]
    }) {
      const providersKey: FilterCategory = `${mediaType}Providers`
      const currentProviders = this.filters[providersKey]
        ? [...this.filters[providersKey]]
        : []
      this.filters[providersKey] = providers.map((provider) => {
        const existingProviderFilterIdx = currentProviders.findIndex(
          (p) => p.code === provider.source_name
        )
        const checked =
          existingProviderFilterIdx >= 0
            ? currentProviders[existingProviderFilterIdx].checked
            : false

        return {
          code: provider.source_name,
          name: provider.display_name,
          checked,
        }
      })
    },
    /**
     * Toggle a filter's checked parameter. Requires either codeIdx or code.
     * Returns the new checked value.
     */
    toggleFilter({
      filterType,
      codeIdx,
      code,
    }: {
      filterType: FilterCategory
      codeIdx?: number
      code?: string
    }): boolean {
      return this.setFilter({ filterType, codeIdx, code, toggle: true })
    },

    /**
     * Set the `checked` parameter of the specific search filter.
     * @param filterType - the slug of the filter kind, e.g. `licenseType`.
     * @param codeIdx - the index of the filter item to set.
     * @param code - the slug code of the filter item, e.g. `commercial`.
     * @param value - the value to set checked to, `true` by default.
     * @param toggle - if `true`, the value will be toggled.
     */
    setFilter({
      filterType,
      codeIdx,
      code,
      value = true,
      toggle = false,
    }: {
      filterType: FilterCategory
      codeIdx?: number
      code?: string
      value?: boolean
      toggle?: boolean
    }) {
      if (typeof codeIdx === "undefined" && typeof code === "undefined") {
        throw new Error(
          `Cannot update filter of type ${filterType}. Use code or codeIdx parameter`
        )
      }
      const filterItems = this.filters[filterType]
      const idx = codeIdx ?? filterItems.findIndex((f) => f.code === code)
      this.filters[filterType][idx].checked = toggle
        ? !this.filters[filterType][idx].checked
        : value
      return this.filters[filterType][idx].checked
    },

    /**
     * Resets all filters to initial values.
     * Provider filters are not in the initial filters, so they need to be
     * handled separately.
     *
     */
    clearFilters() {
      for (const filterCategory of this.filterCategories) {
        for (const filterItem of this.filters[filterCategory]) {
          filterItem.checked = false
        }
      }
    },

    /**
     * After a search type is changed, unchecks all the filters that are not
     * applicable for this Media type.
     */
    clearOtherMediaTypeFilters(searchType: SearchType) {
      const mediaTypesToClear = supportedSearchTypes.filter(
        (type) => type !== searchType
      )
      const filterKeysToClear = mediaTypesToClear.reduce((acc, type) => {
        return [...acc, ...mediaUniqueFilterKeys[type]]
      }, [] as FilterCategory[])

      this.filterCategories.forEach((filterCategory) => {
        if (filterKeysToClear.includes(filterCategory)) {
          this.filters[filterCategory] = this.filters[filterCategory].map(
            (f) => ({ ...f, checked: false })
          )
        }
      })
    },
    /**
     * Replaces filters with the newFilterData object that was created using initial filters,
     * and setting parameters from the search query to checked.
     */
    replaceFilters(newFilterData: Filters) {
      this.filterCategories.forEach((filterCategory) => {
        this.filters[filterCategory] = newFilterData[filterCategory]
      })
    },

    /**
     * Selecting some filter items disables related items. For example, selecting an `nc`
     * license filter (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) disables the `Commercial` license
     * type filter. This function determines if the filter item should be disabled based on
     * the currently checked filter items.
     */
    isFilterDisabled(
      item: FilterItem,
      filterCategory: FilterCategory
    ): boolean {
      if (!["licenseTypes", "licenses"].includes(filterCategory)) {
        return false
      }
      if (item.code === "commercial" || item.code === "modification") {
        const targetCode = {
          commercial: "nc",
          modification: "nd",
        }[item.code]
        return this.filters.licenses.some(
          (item: FilterItem) => item.code.includes(targetCode) && item.checked
        )
      } else {
        const dependentFilters: string[] = []
        if (item.code.includes("nc")) {
          dependentFilters.push("commercial")
        }
        if (item.code.includes("nd")) {
          dependentFilters.push("modification")
        }
        return this.filters.licenseTypes.some(
          (item: FilterItem) =>
            dependentFilters.includes(item.code) && item.checked
        )
      }
    },
  },
})
