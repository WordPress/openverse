import findIndex from 'lodash.findindex'
import local from '~/utils/local'
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_FILTERS,
  SET_FILTERS_FROM_URL,
  SET_FILTER_IS_VISIBLE,
} from '~/store-modules/mutation-types'
import {
  filtersToQueryData,
  queryToFilterData,
} from '~/utils/searchQueryTransform'

const IMAGE_FILTERS = [
  'licenses',
  'licenseTypes',
  'categories',
  'extensions',
  'aspectRatios',
  'sizes',
  'providers',
  'searchBy',
  'mature',
]
export const filterData = {
  licenses: [
    { code: 'cc0', name: 'filters.licenses.cc0', checked: false },
    { code: 'pdm', name: 'filters.licenses.pdm', checked: false },
    { code: 'by', name: 'filters.licenses.by', checked: false },
    { code: 'by-sa', name: 'filters.licenses.by-sa', checked: false },
    { code: 'by-nc', name: 'filters.licenses.by-nc', checked: false },
    { code: 'by-nd', name: 'filters.licenses.by-nd', checked: false },
    { code: 'by-nc-sa', name: 'filters.licenses.by-nc-sa', checked: false },
    { code: 'by-nc-nd', name: 'filters.licenses.by-nc-nd', checked: false },
  ],
  licenseTypes: [
    {
      code: 'commercial',
      name: 'filters.license-types.commercial',
      checked: false,
    },
    {
      code: 'modification',
      name: 'filters.license-types.modification',
      checked: false,
    },
  ],
  categories: [
    {
      code: 'photograph',
      name: 'filters.categories.photograph',
      checked: false,
    },
    {
      code: 'illustration',
      name: 'filters.categories.illustration',
      checked: false,
    },
    {
      code: 'digitized_artwork',
      name: 'filters.categories.digitized-artwork',
      checked: false,
    },
  ],
  extensions: [
    { code: 'jpg', name: 'filters.extensions.jpg', checked: false },
    { code: 'png', name: 'filters.extensions.png', checked: false },
    { code: 'gif', name: 'filters.extensions.gif', checked: false },
    { code: 'svg', name: 'filters.extensions.svg', checked: false },
  ],
  aspectRatios: [
    { code: 'tall', name: 'filters.aspect-ratios.tall', checked: false },
    { code: 'wide', name: 'filters.aspect-ratios.wide', checked: false },
    { code: 'square', name: 'filters.aspect-ratios.square', checked: false },
  ],
  sizes: [
    { code: 'small', name: 'filters.sizes.small', checked: false },
    { code: 'medium', name: 'filters.sizes.medium', checked: false },
    { code: 'large', name: 'filters.sizes.large', checked: false },
  ],
  providers: [],
  searchBy: {
    creator: false,
  },
  mature: false,
}

const isFilterApplied = (filters) =>
  Object.keys(filters).some((filterKey) => {
    if (filterKey === 'searchBy') {
      return filters.searchBy.creator
    } else if (filterKey === 'mature') {
      return false
    } // this is hardcoded to "false" because we do not show mature in `FilterDisplay.vue` like the other filters

    return filters[filterKey].some((filter) => filter.checked)
  })

const state = {
  filters: filterData,
  isFilterVisible: false,
  isFilterApplied: false,
}

const getters = {
  /**
   * Returns all applied filters in unified format
   * Mature filter is not returned because it is not displayed
   * as a filter tag
   * @param state
   * @returns {{code: string, name: string, filterType: string}[]}
   */
  getAppliedFilterTags: (state) => {
    let appliedFilters = []
    Object.keys(state.filters).forEach((filterType) => {
      if (filterType === 'searchBy') {
        if (state.filters.searchBy.creator) {
          appliedFilters.push({
            code: 'creator',
            name: 'filters.searchBy.creator',
            filterType: 'searchBy',
          })
        }
      } else if (filterType !== 'mature') {
        const newFilters = state.filters[filterType]
          .filter((f) => f.checked)
          .map((f) => {
            return {
              code: f.code,
              name: f.name,
              filterType: filterType,
            }
          })
        appliedFilters = [...appliedFilters, ...newFilters]
      }
    })
    return appliedFilters
  },
  getAllImageFilters: (state) => {
    let allImageFilters = {}
    Object.keys(state.filters).forEach((filterType) => {
      if (IMAGE_FILTERS.includes(filterType)) {
        if (filterType === 'searchBy') {
          allImageFilters[filterType] = [
            {
              code: 'creator',
              name: 'filters.creator.title',
              filterType: 'searchBy',
              checked: state.filters.searchBy.creator,
            },
          ]
        } else if (filterType !== 'mature') {
          const newFilters = state.filters[filterType].map((f) => {
            return {
              code: f.code,
              name: f.name,
              filterType: filterType,
              checked: f.checked,
            }
          })
          allImageFilters[filterType] = newFilters
        }
      }
    })
    console.log('getimagefilters returns ', allImageFilters)
    return allImageFilters
  },
}

const actions = {
  [TOGGLE_FILTER]({ commit, state }, params) {
    const { filterType, code } = params
    const filters = state.filters[filterType]
    const codeIdx = findIndex(filters, (f) => f.code === code)

    commit(SET_FILTER, { codeIdx, ...params })
  },
}

function setQuery(state) {
  const query = filtersToQueryData(state.filters)

  state.isFilterApplied = isFilterApplied(state.filters)
  state.query = {
    q: state.query.q,
    ...query,
  }
}

function replaceFilters(state, filterData) {
  Object.keys(state.filters).forEach((filterType) => {
    if (filterType === 'mature') {
      state.filters.mature = filterData.mature
    } else if (filterType === 'searchBy') {
      state.filters.searchBy.creator = filterData.searchBy.creator
    } else if (filterType === 'providers') {
      filterData.providers.forEach((provider) => {
        const idx = state.filters.providers.findIndex(
          (p) => p.code === provider.code
        )
        state.filters.providers[idx].checked = provider.checked
      })
    } else {
      state.filters[filterType] = filterData[filterType]
    }
  })
}

function setFilter(state, params) {
  const { filterType, codeIdx } = params
  if (filterType === 'searchBy') {
    state.filters.searchBy.creator = !state.filters.searchBy.creator
  } else if (filterType === 'mature') {
    state.filters.mature = !state.filters.mature
  } else {
    const filters = state.filters[filterType]
    filters[codeIdx].checked = !filters[codeIdx].checked
  }

  setQuery(state, params)
}

// Make sure when redirecting after applying a filter, we stick to the right tab (i.e, "/search/video", "/search/audio", etc.)
const mutations = {
  [SET_FILTERS_FROM_URL](state, params) {
    replaceFilters(state, queryToFilterData(params.url))
    state.isFilterApplied = isFilterApplied(state.filters)
  },
  [SET_FILTER](state, params) {
    return setFilter(state, params)
  },
  [CLEAR_FILTERS](state) {
    const initialFilters = filterData
    const resetProviders = state.filters.providers.map((provider) => ({
      ...provider,
      checked: false,
    }))
    state.filters = {
      ...initialFilters,
      providers: resetProviders,
    }
    return setQuery(state)
  },
  [SET_PROVIDERS_FILTERS](state, params) {
    const providers = params.imageProviders
    // merge providers from API response with the filters that came from the
    // browse URL search query string and match the checked properties
    // in the store
    state.filters.providers = providers.map((provider) => {
      const existingProviderFilterIdx = findIndex(
        state.filters.providers,
        (p) => p.code === provider.source_name
      )

      const checked =
        existingProviderFilterIdx >= 0
          ? state.filters.providers[existingProviderFilterIdx].checked
          : false

      return {
        code: provider.source_name,
        name: provider.display_name,
        checked,
      }
    })
  },
  [SET_FILTER_IS_VISIBLE](state, params) {
    state.isFilterVisible = params.isFilterVisible
    local.set(process.env.filterStorageKey, params.isFilterVisible)
  },
}

export default {
  state,
  getters,
  actions,
  mutations,
}
