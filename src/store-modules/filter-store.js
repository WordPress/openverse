import findIndex from 'lodash.findindex'
import { ExperimentData } from '../abTests/experiments/filterExpansion'
import local from '../utils/local'
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

const FILTER_STATE_STORAGE_KEY = 'ccsearch-filter-visibility'
const MIN_SCREEN_WIDTH_FILTER_VISIBLE_BY_DEFAULT = 800
const isDesktop = () =>
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

const localfilterState = () =>
  local.get(FILTER_STATE_STORAGE_KEY)
    ? local.get(FILTER_STATE_STORAGE_KEY) === 'true'
    : true

const initialState = (searchParams) => {
  const filters = queryToFilterData(searchParams)

  const isFilterVisible = isDesktop() ? localfilterState() : false
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

// Make sure when redirecting after applying a filter, we stick to the right tab (i.e, "/search/video", "/search/audio", etc.)
const mutations = (redirect) => ({
  [SET_FILTER](state, params) {
    return setFilter(state, params, window.location.pathname, redirect)
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
    return setQuery(state, params, window.location.pathname, redirect)
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
    local.set(FILTER_STATE_STORAGE_KEY, params.isFilterVisible)
  },
})

export default {
  state: initialState,
  actions,
  mutations,
}
