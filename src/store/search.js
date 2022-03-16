import {
  filtersToQueryData,
  queryStringToSearchType,
} from '~/utils/search-query-transform'
import { ALL_MEDIA } from '~/constants/media'
import {
  UPDATE_QUERY,
  SET_SEARCH_STATE_FROM_URL,
  TOGGLE_FILTER,
  UPDATE_QUERY_FROM_FILTERS,
  CLEAR_FILTERS,
} from '~/constants/action-types'
import { SET_QUERY, SET_SEARCH_TYPE } from '~/constants/mutation-types'

import { useFilterStore } from '~/stores/filter'

/**
 * `query` has the API request parameters for search filtering. Locally, some filters
 * have different names, and some query parameters correspond to different filter parameters
 * depending on the media type. For example, `extension` query parameter can be `audioExtension`
 * or `imageExtension`, with different values for each.
 *
 * @return {import('./types').SearchState}
 */
export const state = () => ({
  searchType: ALL_MEDIA,
  query: {
    q: '',
    license_type: '',
    license: '',
    categories: '',
    extension: '',
    duration: '',
    aspect_ratio: '',
    size: '',
    source: '',
    searchBy: '',
    mature: '',
  },
})

export const getters = {
  /**
   * Returns the search query parameters for API request:
   * drops all parameters with blank values.
   * @param {import('./types').SearchState} state
   * @return {import('./types').ApiQueryParams}
   */
  searchQueryParams: (state) => {
    // Ensure that q filter always comes first
    const params = { q: state.query.q.trim() }
    // Handle mature filter separately
    const filterKeys = Object.keys(state.query).filter(
      (key) => !['q', 'mature'].includes(key)
    )
    filterKeys.forEach((key) => {
      if (state.query[key].length) {
        params[key] = state.query[key]
      }
    })
    if (state.query.mature === true) {
      params.mature = true
    }
    return params
  },
  searchFilters: (state) => {
    return useFilterStore().getMediaTypeFilters({ mediaType: state.searchType })
  },
}

const actions = {
  /**
   * Called when `q` search term or `searchType` are changed.
   * @param {import('vuex').ActionContext} context
   * @param {import('vuex').ActionPayload} params
   * @param {string} [params.q]
   * @param {import('./types').SupportedSearchType} [params.searchType]
   * @return {Promise<void>}
   */
  async [UPDATE_QUERY]({ commit, dispatch, state }, params = {}) {
    const { q, searchType } = params
    /** @type {{ q: string? }} */
    const queryParams = {}
    if (q) {
      queryParams.q = q.trim()
    }
    if (searchType && searchType !== state.searchType) {
      commit(SET_SEARCH_TYPE, { searchType })
      useFilterStore().clearOtherMediaTypeFilters({ searchType })
    }
    await dispatch(UPDATE_QUERY_FROM_FILTERS, queryParams)
  },
  /**
   * Toggles a filter's checked parameter
   * @param {import('vuex').ActionContext} context
   * @param params
   */
  async [TOGGLE_FILTER]({ dispatch }, params) {
    useFilterStore().toggleFilter(params)
    await dispatch(UPDATE_QUERY_FROM_FILTERS)
  },

  /**
   * Resets all filters to initial values.
   * Provider filters are not in the initial filters, so they need to be
   * handled separately.
   * @param {import('vuex').ActionContext} context
   */
  async [CLEAR_FILTERS]({ dispatch }) {
    useFilterStore().clearFilters()
    await dispatch(UPDATE_QUERY_FROM_FILTERS, { q: '' })
  },

  /**
   * Called when a /search path is server-rendered.
   * @param {import('vuex').ActionContext} context
   * @param {string} path
   * @param {Object} query
   */
  async [SET_SEARCH_STATE_FROM_URL]({ commit, dispatch }, { path, query }) {
    const searchType = queryStringToSearchType(path)
    const queryParams = {}
    if (query.q) {
      queryParams.q = query.q
    }

    commit(SET_SEARCH_TYPE, { searchType })
    useFilterStore().updateFiltersFromUrl(query, searchType)

    await dispatch(UPDATE_QUERY_FROM_FILTERS, queryParams)
  },
  /**
   * After a change in filters, updates the query.
   * @param {import('vuex').ActionContext} context
   * @param {Object} params
   * @param {string} [params.q]
   * @param {'audio'|'image'} [params.mediaType]
   */
  async [UPDATE_QUERY_FROM_FILTERS]({ state, commit }, params = {}) {
    const queryFromFilters = filtersToQueryData(
      useFilterStore().filters,
      params.mediaType || state.searchType,
      true
    )

    // If the filter was unchecked, its value in `queryFromFilters` would be falsy, ''.
    // So we check if the key exists, not if the value is not falsy.
    const changedKeys = Object.keys(queryFromFilters)
    const updatedQuery = /** @type {import('../store/types').Query} */ (
      Object.keys(state.query).reduce((obj, key) => {
        if (key === 'q') {
          obj[key] = params?.q || state.query.q
        } else {
          obj[key] = changedKeys.includes(key) ? queryFromFilters[key] : ''
        }
        return obj
      }, {})
    )
    commit(SET_QUERY, { query: updatedQuery })
  },
}

const mutations = {
  /**
   * Sets the content type to search.
   * @param {import('./types').SearchState} state
   * @param {import('../constants/media').SearchType} searchType
   */
  [SET_SEARCH_TYPE](state, { searchType }) {
    state.searchType = searchType
    useFilterStore().setSearchType(searchType)
  },
  /**
   * Replaces the query object that is used for API calls.
   * @param {import('./types').SearchState} state
   * @param {Object} query
   */
  [SET_QUERY](state, { query }) {
    state.query = query
  },
}

export default {
  state,
  getters,
  actions,
  mutations,
}
