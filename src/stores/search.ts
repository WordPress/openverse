import { defineStore } from 'pinia'
import {
  computed,
  ComputedRef,
  reactive,
  toRefs,
  watch,
} from '@nuxtjs/composition-api'
// We plan to remove this dependency, so don't need to add types for it:
// https://github.com/WordPress/openverse-frontend/issues/1103
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import clonedeep from 'lodash.clonedeep'

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedSearchTypes,
} from '~/constants/media'
import {
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
import type { SupportedSearchType } from '~/constants/media'
import type { ApiQueryParams } from '~/store/types'

export const useSearchStore = defineStore('search', () => {
  const state: {
    searchType: SupportedSearchType
    searchTerm: string
    filters: Filters
  } = reactive({
    searchType: ALL_MEDIA,
    searchTerm: '',
    filters: clonedeep(filterData),
  })
  const { filters, searchType, searchTerm } = toRefs(state)

  // Setters
  const setSearchType = (type: SupportedSearchType) => {
    state.searchType = type
  }
  function setSearchTerm(term: string) {
    state.searchTerm = term.trim()
  }
  watch(searchType, (searchType) => clearOtherMediaTypeFilters(searchType))

  // Getters
  /**
   * Returns the search query parameters for API request:
   * drops all parameters with blank values.
   */
  const searchQueryParams: ComputedRef<ApiQueryParams> = computed(() => {
    return computeQueryParams(searchType.value, filters.value)
  })

  const computeQueryParams = (
    searchType: SupportedSearchType,
    filters: Filters = state.filters
  ) => {
    const query = { ...filtersToQueryData(filters, searchType) }

    const queryKeys = Object.keys(query) as (keyof ApiQueryParams)[]
    return queryKeys.reduce(
      (obj, key: keyof ApiQueryParams) => {
        if (key !== 'q' && query[key]?.length) {
          obj[key] = query[key]
        }
        return obj
      },
      // Ensure that q filter always comes first
      { q: state.searchTerm.trim() } as ApiQueryParams
    )
  }

  const allFilterCategories = Object.keys(state.filters) as FilterCategory[]
  /**
   * Initial filters do not include the provider filters. We create the provider filters object
   * when we fetch the provider data on the Nuxt server initialization.
   * We call this function to reset the filters to the initial base filters AND the provider filters.
   */
  const getBaseFiltersWithProviders = (): Filters => {
    const resetProviders = (mediaType: SupportedMediaType): FilterItem[] => {
      return state.filters[`${mediaType}Providers`].map((provider) => ({
        ...provider,
        checked: false,
      }))
    }
    return {
      ...clonedeep(filterData),
      audioProviders: resetProviders(AUDIO),
      imageProviders: resetProviders(IMAGE),
    }
  }

  /**
   * Returns the number of checked filters, excluding the `mature` filter.
   */
  const appliedFilterCount: ComputedRef<number> = computed(() => {
    const filterKeys = mediaFilterKeys[state.searchType].filter(
      (f) => f !== 'mature'
    )
    return filterKeys.reduce((count, filterCategory) => {
      return (
        count + state.filters[filterCategory].filter((f) => f.checked).length
      )
    }, 0)
  })

  /**
   * True if any filter for selected search type except `mature` is checked.
   */
  const isAnyFilterApplied: ComputedRef<boolean> = computed(() => {
    const filterEntries = Object.entries(searchFilters.value) as [
      string,
      FilterItem[]
    ][]
    return filterEntries.some(
      ([filterKey, filterItems]) =>
        filterKey !== 'mature' && filterItems.some((filter) => filter.checked)
    )
  })

  // Actions
  /**
   * After a search type is changed, unchecks all the filters that are not
   * applicable for this Media type.
   */
  function clearOtherMediaTypeFilters(searchType: SupportedSearchType) {
    const mediaTypesToClear = supportedSearchTypes.filter(
      (type) => type !== searchType
    )
    const filterKeysToClear = mediaTypesToClear.reduce((acc, type) => {
      return [...acc, ...mediaUniqueFilterKeys[type]]
    }, [] as FilterCategory[])

    allFilterCategories.forEach((filterCategory) => {
      if (filterKeysToClear.includes(filterCategory)) {
        state.filters[filterCategory] = state.filters[filterCategory].map(
          (f) => ({
            ...f,
            checked: false,
          })
        )
      }
    })
  }

  /**
   * Replaces filters with the newFilterData object that was created using initial filters,
   * and setting parameters from the search query to checked.
   *
   *
   *
   */
  function replaceFilters(newFilterData: Filters) {
    allFilterCategories.forEach((filterCategory) => {
      state.filters[filterCategory] = newFilterData[filterCategory]
    })
  }

  /**
   * Merge providers from API response with the filters that came from the browse URL search query string
   * and match the checked properties in the store.
   */
  function initProviderFilters({
    mediaType,
    providers,
  }: {
    mediaType: SupportedMediaType
    providers: { source_name: string; display_name: string }[]
  }) {
    const providersKey: FilterCategory = `${mediaType}Providers`
    const currentProviders = state.filters[providersKey]
      ? [...state.filters[providersKey]]
      : []
    state.filters[providersKey] = providers.map((provider) => {
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
  }
  /**
   * Toggles a filter's checked parameter. Requires either codeIdx or code.
   */
  function toggleFilter({
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
    const filterItems = state.filters[filterType]
    const idx = codeIdx ?? filterItems.findIndex((f) => f.code === code)
    state.filters[filterType][idx].checked = !filterItems[idx].checked
  }

  /**
   * Resets all filters to initial values.
   * Provider filters are not in the initial filters, so they need to be
   * handled separately.
   *
   */
  const clearFilters = () => {
    for (const filterCategory of Object.keys(
      state.filters
    ) as FilterCategory[]) {
      for (const filterItem of state.filters[filterCategory]) {
        filterItem.checked = false
      }
    }
  }

  /**
   * Selecting some filter items disables related items. For example, selecting an `nc`
   * license filter (CC BY-NC, CC BY-NC-SA, CC BY-NC-ND) disables the `Commercial` license
   * type filter. This function determines if the filter item should be disabled based on
   * the currently checked filter items.
   */
  function isFilterDisabled(
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
      return state.filters.licenses.some(
        (item) => item.code.includes(targetCode) && item.checked
      )
    } else {
      const dependentFilters: string[] = []
      if (item.code.includes('nc')) {
        dependentFilters.push('commercial')
      }
      if (item.code.includes('nd')) {
        dependentFilters.push('modification')
      }
      return state.filters.licenseTypes.some(
        (item) => dependentFilters.includes(item.code) && item.checked
      )
    }
  }

  /**
   * Returns the object with filters for selected search type, with codes, names for i18n labels, and checked status.
   */
  const searchFilters: ComputedRef<Filters> = computed(() => {
    return mediaFilterKeys[state.searchType]
      .filter((filterKey) => filterKey !== 'mature')
      .reduce((obj, filterKey) => {
        obj[filterKey] = state.filters[filterKey]
        return obj
      }, {} as Filters)
  })

  /**
   * Called when a /search path is server-rendered.
   */
  function setSearchStateFromUrl({
    path,
    urlQuery,
  }: {
    path: string
    urlQuery: Record<string, string>
  }) {
    if (urlQuery.q) {
      setSearchTerm(urlQuery.q.trim())
    }
    state.searchType = queryStringToSearchType(path)
    // When setting filters from URL query, 'mature' has a value of 'true',
    // but we need the 'mature' code. Creating a local shallow copy to prevent mutation.
    const query = { ...urlQuery }
    if (query.mature === 'true') {
      query.mature = 'mature'
    } else {
      delete query.mature
    }

    const newFilterData = queryToFilterData({
      query,
      searchType: state.searchType,
      defaultFilters: getBaseFiltersWithProviders(),
    })
    replaceFilters(newFilterData)
  }

  return {
    searchTerm,
    searchType,
    filters,

    appliedFilterCount,
    isAnyFilterApplied,
    searchFilters,
    searchQueryParams,

    setSearchTerm,
    setSearchType,
    setSearchStateFromUrl,
    initProviderFilters,
    isFilterDisabled,
    clearFilters,
    toggleFilter,
    computeQueryParams,
  }
})
