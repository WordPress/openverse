import findIndex from 'lodash.findindex'
import { ExperimentData } from '@/abTests/experiments/filterExpansion'
import { TOGGLE_FILTER, CONVERT_AB_TEST_EXPERIMENT } from './action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_FILTERS,
  SET_FILTER_IS_VISIBLE,
} from './mutation-types'
import {
  queryToFilterData,
  filtersToQueryData,
} from '../utils/searchQueryTransform'
import { screenWidth } from '../utils/getBrowserInfo'

export const filterData = {
  licenses: [
    { code: 'cc0', name: 'CC0', checked: false },
    { code: 'pdm', name: 'Public Domain Mark', checked: false },
    { code: 'by', name: 'BY', checked: false },
    { code: 'by-sa', name: 'BY-SA', checked: false },
    { code: 'by-nc', name: 'BY-NC', checked: false },
    { code: 'by-nd', name: 'BY-ND', checked: false },
    { code: 'by-nc-sa', name: 'BY-NC-SA', checked: false },
    { code: 'by-nc-nd', name: 'BY-NC-ND', checked: false },
  ],
  licenseTypes: [
    { code: 'commercial', name: 'Use commercially', checked: false },
    { code: 'modification', name: 'Modify or adapt', checked: false },
  ],
  categories: [
    { code: 'photograph', name: 'Photographs', checked: false },
    { code: 'illustration', name: 'Illustrations', checked: false },
    { code: 'digitized_artwork', name: 'Digitized Artworks', checked: false },
  ],
  extensions: [
    { code: 'jpg', name: 'JPEGs', checked: false },
    { code: 'png', name: 'PNGs', checked: false },
    { code: 'gif', name: 'GIFs', checked: false },
    { code: 'svg', name: 'SVGs', checked: false },
  ],
  aspectRatios: [
    { code: 'tall', name: 'Tall', checked: false },
    { code: 'wide', name: 'Wide', checked: false },
    { code: 'square', name: 'Square', checked: false },
  ],
  sizes: [
    { code: 'small', name: 'Small', checked: false },
    { code: 'medium', name: 'Medium', checked: false },
    { code: 'large', name: 'Large', checked: false },
  ],
  providers: [],
  searchBy: {
    creator: false,
  },
  mature: false,
}

const MIN_SCREEN_WIDTH_FILTER_VISIBLE_BY_DEFAULT = 800
const hideFiltersIfMobileScreen = () =>
  screenWidth() > MIN_SCREEN_WIDTH_FILTER_VISIBLE_BY_DEFAULT

const isFilterApplied = (filters) =>
  Object.keys(filters).some((filterKey) => {
    if (filterKey === 'searchBy') {
      return filters.searchBy.creator
    } else if (filterKey === 'mature') {
      return false
    } // this is hardcoded to "false" because we do not show mature in `FilterDisplay.vue` like the other filters

    return filters[filterKey].some((filter) => filter.checked)
  })

const initialState = (searchParams) => {
  const filters = queryToFilterData(searchParams)

  const isFilterVisible = hideFiltersIfMobileScreen()
  const filtersApplied = isFilterApplied(filters)
  return {
    filters,
    isFilterVisible,
    isFilterApplied: filtersApplied,
  }
}

const actions = {
  [TOGGLE_FILTER]({ commit, state, dispatch }, params) {
    const filters = state.filters[params.filterType]
    const codeIdx = findIndex(filters, (f) => f.code === params.code)

    commit(SET_FILTER, {
      codeIdx,
      ...params,
    })

    dispatch(CONVERT_AB_TEST_EXPERIMENT, {
      experimentName: ExperimentData.EXPERIMENT_NAME,
    })
  },
}

function setQuery(state, params, path, redirect) {
  const query = filtersToQueryData(state.filters)
  state.isFilterApplied = isFilterApplied(state.filters)
  state.query = {
    q: state.query.q,
    ...query,
  }
  if (params.shouldNavigate === true) {
    redirect({ path, query: state.query })
  }
}

function setFilter(state, params, path, redirect) {
  if (params.filterType === 'searchBy') {
    state.filters.searchBy.creator = !state.filters.searchBy.creator
  } else if (params.filterType === 'mature') {
    state.filters.mature = !state.filters.mature
  } else {
    const filters = state.filters[params.filterType]
    filters[params.codeIdx].checked = !filters[params.codeIdx].checked
  }

  setQuery(state, params, path, redirect)
}

const redirectUrl = (params) =>
  params.isCollectionsPage ? `/collections/${params.provider}` : '/search'

const mutations = (redirect) => ({
  [SET_FILTER](state, params) {
    return setFilter(state, params, redirectUrl(params), redirect)
  },
  [CLEAR_FILTERS](state, params) {
    const initialFilters = initialState('').filters
    const resetProviders = state.filters.providers.map((provider) => ({
      ...provider,
      checked: false,
    }))
    state.filters = {
      ...initialFilters,
      providers: resetProviders,
    }
    return setQuery(state, params, redirectUrl(params), redirect)
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
  },
})

export default {
  state: initialState,
  actions,
  mutations,
}
