import { defineStore } from 'pinia'

import { deepClone } from '~/utils/clone'
import type { DeepWriteable } from '~/types/utils'

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  SearchType,
  SupportedMediaType,
  SupportedSearchType,
  supportedSearchTypes,
} from '~/constants/media'
import {
  ApiQueryParams,
  filtersToQueryData,
  queryStringToSearchType,
  queryToFilterData,
} from '~/utils/search-query-transform'
import {
  FilterCategory,
  FilterItem,
  Filters,
  filterData,
  mediaFilterKeys,
  mediaUniqueFilterKeys,
} from '~/constants/filters'

import type { Dictionary } from 'vue-router/types/router'

export const isSearchTypeSupported = (
  st: SearchType
): st is SupportedSearchType => {
  return supportedSearchTypes.includes(st as SupportedSearchType)
}

export interface SearchState {
  searchType: SearchType
  searchTerm: string
  filters: Filters
}

function computeQueryParams(
  searchType: SupportedSearchType,
  filters: Filters,
  searchTerm: string
) {
  const query = { ...filtersToQueryData(filters, searchType) }

  const queryKeys = Object.keys(query) as (keyof ApiQueryParams)[]

  return queryKeys.reduce(
    (obj, key) => {
      if (key !== 'q' && query[key]?.length) {
        obj[key] = query[key]
      }
      return obj
    },
    // Ensure that q filter always comes first
    { q: searchTerm.trim() } as ApiQueryParams
  )
}

export const useSearchStore = defineStore('search', {
  state: (): SearchState => ({
    searchType: ALL_MEDIA,
    searchTerm: '',
    filters: deepClone(filterData as DeepWriteable<typeof filterData>),
  }),
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
        (f) => f !== 'mature'
      )
      return filterKeys.reduce((count, filterCategory) => {
        return (
          count + state.filters[filterCategory].filter((f) => f.checked).length
        )
      }, 0)
    },
    /**
     * Returns the object with filters for selected search type, with codes, names for i18n labels, and checked status.
     */
    searchFilters(state) {
      return mediaFilterKeys[state.searchType]
        .filter((filterKey) => filterKey !== 'mature')
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
          filterKey !== 'mature' && filterItems.some((filter) => filter.checked)
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
    setSearchType(type: SupportedSearchType) {
      this.searchType = type
      this.clearOtherMediaTypeFilters(type)
    },
    setSearchTerm(term: string) {
      this.searchTerm = term.trim()
    },
    computeQueryParams(type: SupportedSearchType) {
      return computeQueryParams(type, this.filters, this.searchTerm)
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
    /**
     * Merge providers from API response with the filters that came from the browse URL search query string
     * and match the checked properties in the store.
     */
    initProviderFilters({
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
      if (typeof codeIdx === 'undefined' && typeof code === 'undefined') {
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
    clearOtherMediaTypeFilters(searchType: SupportedSearchType) {
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
      urlQuery: Dictionary<string | (string | null)[]>
    }) {
      if (urlQuery.q && typeof urlQuery.q === 'string') {
        this.setSearchTerm(urlQuery.q.trim())
      }
      this.searchType = queryStringToSearchType(path)
      if (!isSearchTypeSupported(this.searchType)) return
      // When setting filters from URL query, 'mature' has a value of 'true',
      // but we need the 'mature' code. Creating a local shallow copy to prevent mutation.
      const query = { ...urlQuery }
      if (query.mature === 'true') {
        query.mature = 'mature'
      } else {
        delete query.mature
      }

      const newFilterData = queryToFilterData({
        query: query as Record<string, string>,
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
      if (!['licenseTypes', 'licenses'].includes(filterCategory)) {
        return
      }
      if (item.code === 'commercial' || item.code === 'modification') {
        const targetCode = {
          commercial: 'nc',
          modification: 'nd',
        }[item.code]
        return this.filters.licenses.some(
          (item: FilterItem) => item.code.includes(targetCode) && item.checked
        )
      } else {
        const dependentFilters: string[] = []
        if (item.code.includes('nc')) {
          dependentFilters.push('commercial')
        }
        if (item.code.includes('nd')) {
          dependentFilters.push('modification')
        }
        return this.filters.licenseTypes.some(
          (item: FilterItem) =>
            dependentFilters.includes(item.code) && item.checked
        )
      }
    },
  },
})
