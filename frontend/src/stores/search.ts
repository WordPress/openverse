import { useLocalePath } from "#imports"

import { defineStore } from "pinia"

import { useStorage } from "@vueuse/core"

import { LocationQuery } from "vue-router"

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

import {
  SearchQuery,
  SearchStrategy,
  PaginatedSearchQuery,
  CollectionParams,
  PaginatedCollectionQuery,
} from "~/types/search"

import type { Ref } from "vue"

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

/**
 * Builds the search query parameters for the given search type, filters, and search term.
 * `q` parameter is always included as the first query parameter.
 * If the search type is not supported, only the `q` parameter is included.
 * This is used, for instance, for content switcher links for `video`/`model_3d` search pages.
 * Only the filters that are relevant for the search type and have a value are included.
 *
 * `INCLUDE_SENSITIVE_QUERY_PARAM` is never added to the frontend search query. It is added
 * to the API search query if the setting is `on` in the featureFlagStore.
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
  }

  // `INCLUDE_SENSITIVE_QUERY_PARAM` is used in the API params, but not shown on the frontend.
  const ffStore = useFeatureFlagStore()
  if (mode === "API" && ffStore.isOn("fetch_sensitive")) {
    searchQuery[INCLUDE_SENSITIVE_QUERY_PARAM] = "true"
  }

  return searchQuery
}

export function collectionToPath(collectionParams: CollectionParams) {
  switch (collectionParams.collection) {
    case "tag": {
      return `tag/${collectionParams.tag}/`
    }
    case "creator": {
      return `source/${collectionParams.source}/creator/${collectionParams.creator}/`
    }
    case "source": {
      return `source/${collectionParams.source}/`
    }
  }
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
        FilterItem[]
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
  },
  actions: {
    getSearchUrlParts(mediaType: SupportedMediaType) {
      const query: PaginatedSearchQuery | PaginatedCollectionQuery =
        this.strategy === "default"
          ? computeQueryParams(mediaType, this.filters, this.searchTerm, "API")
          : {}
      const pathSlug =
        this.collectionParams === null
          ? ""
          : collectionToPath(this.collectionParams)
      return { query, pathSlug }
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
      return useLocalePath()({
        path: searchPath(searchType),
        query: queryParams as unknown as LocationQuery,
      })
    },

    /**
     * Returns localized frontend path for the given collection.
     * Does not support query parameters for now.
     */
    getCollectionPath({
      type,
      collectionParams,
    }: {
      type: SupportedMediaType
      collectionParams: CollectionParams
    }) {
      const path = `/${type}/${collectionToPath(collectionParams)}`
      return useLocalePath()(path)
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

      const mediaStore = useMediaStore()
      mediaStore.clearMedia()
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
    setCollectionState(
      collectionParams: CollectionParams,
      mediaType: SupportedMediaType
    ) {
      this.collectionParams = collectionParams
      this.strategy = collectionParams?.collection
      this.setSearchType(mediaType)
      this.clearFilters()
    },
    /**
     * Called when a /search path is server-rendered.
     */
    setSearchStateFromUrl({
      path,
      urlQuery,
    }: {
      path: string
      urlQuery: LocationQuery
    }) {
      // Update `fetch_sensitive` from the feature flag store because
      // the value is not present in the URL.
      const ffStore = useFeatureFlagStore()
      const query = queryDictionaryToQueryParams({
        ...urlQuery,
        ...(ffStore.isOn("fetch_sensitive")
          ? { [INCLUDE_SENSITIVE_QUERY_PARAM]: "true" }
          : {}),
      })

      this.strategy = "default"

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
