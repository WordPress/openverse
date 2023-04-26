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
  ApiQueryParams,
  filtersToQueryData,
  qToSearchTerm,
  queryStringToSearchType,
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

import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"

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
  recentSearches: Ref<string[]>
  searchTerm: string
  localSearchTerm: string
  filters: Filters
}

function computeQueryParams(
  searchType: SearchType,
  filters: Filters,
  searchTerm: string
) {
  const query = { ...filtersToQueryData(filters, searchType) }

  const queryKeys = Object.keys(query) as (keyof ApiQueryParams)[]

  return queryKeys.reduce(
    (obj, key) => {
      if (key !== "q" && query[key]?.length) {
        obj[key] = query[key]
      }
      return obj
    },
    // Ensure that q filter always comes first
    { q: searchTerm.trim() } as ApiQueryParams
  )
}

export const useSearchStore = defineStore("search", {
  state: (): SearchState => ({
    searchType: ALL_MEDIA,
    searchTerm: "",
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
     * Returns the search query parameters for API request:
     * drops all parameters with blank values.
     */
    searchQueryParams(state) {
      if (isSearchTypeSupported(state.searchType)) {
        return computeQueryParams(
          state.searchType,
          state.filters,
          state.searchTerm
        )
      } else {
        return { q: state.searchTerm }
      }
    },

    /**
     * Returns the number of checked filters, excluding the `mature` filter.
     */
    appliedFilterCount(state) {
      const filterKeys = mediaFilterKeys[state.searchType].filter(
        (f) => f !== "mature"
      )
      return filterKeys.reduce((count, filterCategory) => {
        return (
          count + state.filters[filterCategory].filter((f) => f.checked).length
        )
      }, 0)
    },

    /**
     * Returns the object with filters for selected search type,
     * with codes, names for i18n labels, and checked status.
     *
     * Excludes `searchBy` and `mature` filters that we don't display.
     */
    searchFilters(state) {
      return mediaFilterKeys[state.searchType]
        .filter((filterKey) => !["searchBy", "mature"].includes(filterKey))
        .reduce((obj, filterKey) => {
          obj[filterKey] = this.filters[filterKey]
          return obj
        }, {} as Filters)
    },

    /**
     * True if any filter for selected search type except `mature` is checked.
     */
    isAnyFilterApplied() {
      const filterEntries = Object.entries(this.searchFilters) as [
        string,
        FilterItem[]
      ][]
      return filterEntries.some(
        ([filterKey, filterItems]) =>
          filterKey !== "mature" && filterItems.some((filter) => filter.checked)
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
     * Returns localized search path for the given search type.
     *
     * If search type is not provided, returns the path for the current search type.
     * If query is not provided, returns current query parameters.
     */
    getSearchPath({
      type,
      query,
    }: { type?: SearchType; query?: ApiQueryParams } = {}): string {
      const searchType = type || this.searchType
      let queryParams
      if (!query) {
        if (type && isSearchTypeSupported(type)) {
          queryParams = computeQueryParams(type, this.filters, this.searchTerm)
        } else {
          queryParams = this.searchQueryParams
        }
      } else {
        queryParams = query
      }

      return this.$nuxt.localePath({
        path: searchPath(searchType),
        query: queryParams as Dictionary<string>,
      })
    },
    setSearchType(type: SearchType) {
      const featureFlagStore = useFeatureFlagStore()
      if (
        !featureFlagStore.isOn("external_sources") &&
        isAdditionalSearchType(type)
      ) {
        throw new Error(
          `Please enable the 'external_sources' flag to use the ${type}`
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
    setSearchTerm(q: string | (null | string)[] | null) {
      const formattedTerm = qToSearchTerm(q)
      if (this.searchTerm === formattedTerm) return
      this.searchTerm = formattedTerm
      this.localSearchTerm = formattedTerm

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
    computeQueryParams(type: SupportedSearchType) {
      return computeQueryParams(type, this.filters, this.searchTerm)
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
     * Toggles a filter's checked parameter. Requires either codeIdx or code.
     */
    toggleFilter({
      filterType,
      codeIdx,
      code,
    }: {
      filterType: FilterCategory
      codeIdx?: number
      code?: string
    }) {
      if (typeof codeIdx === "undefined" && typeof code === "undefined") {
        throw new Error(
          `Cannot toggle filter of type ${filterType}. Use code or codeIdx parameter`
        )
      }
      const filterItems = this.filters[filterType]
      const idx = codeIdx ?? filterItems.findIndex((f) => f.code === code)
      this.filters[filterType][idx].checked = !filterItems[idx].checked
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
     * Called when a /search path is server-rendered.
     */
    setSearchStateFromUrl({
      path,
      urlQuery,
    }: {
      path: string
      urlQuery: Context["query"]
    }) {
      this.setSearchTerm(urlQuery.q)
      this.searchType = queryStringToSearchType(path)
      if (!isSearchTypeSupported(this.searchType)) return
      // When setting filters from URL query, 'mature' has a value of 'true',
      // but we need the 'mature' code. Creating a local shallow copy to prevent mutation.
      const query: Record<string, string> = { ...urlQuery, q: this.searchTerm }
      if (query.mature === "true") {
        query.mature = "mature"
      } else {
        delete query.mature
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
    ): boolean | undefined {
      if (!["licenseTypes", "licenses"].includes(filterCategory)) {
        return
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
