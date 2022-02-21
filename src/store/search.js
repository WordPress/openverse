import findIndex from 'lodash.findindex'
import clonedeep from 'lodash.clonedeep'

import {
  filtersToQueryData,
  queryStringToSearchType,
  queryToFilterData,
} from '~/utils/search-query-transform'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  supportedSearchTypes,
  VIDEO,
} from '~/constants/media'
import {
  UPDATE_QUERY,
  SET_SEARCH_STATE_FROM_URL,
  TOGGLE_FILTER,
  UPDATE_QUERY_FROM_FILTERS,
  CLEAR_FILTERS,
} from '~/constants/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_OTHER_MEDIA_TYPE_FILTERS,
  REPLACE_FILTERS,
  SET_QUERY,
  SET_SEARCH_TYPE,
} from '~/constants/mutation-types'

/**
 * List of filters available for each search type. The order of the keys
 * is the same as in the filter checklist display (sidebar or modal).
 */
export const mediaFilterKeys = {
  [IMAGE]: [
    'licenseTypes',
    'licenses',
    'imageCategories',
    'imageExtensions',
    'aspectRatios',
    'sizes',
    'imageProviders',
    'searchBy',
    'mature',
  ],
  [AUDIO]: [
    'licenseTypes',
    'licenses',
    'audioCategories',
    'audioExtensions',
    'durations',
    'audioProviders',
    'searchBy',
    'mature',
  ],
  [VIDEO]: [],
  [ALL_MEDIA]: ['licenseTypes', 'licenses', 'searchBy', 'mature'],
}
const createInitialFilters = (category, items) =>
  items.map((item) => ({
    code: item,
    name: `filters.${category}.${item}`,
    checked: false,
  }))

/**
 * A list of filters that are only used for the specific content type.
 * This is used to clear filters from other content types when changing the content type.
 */
export const mediaSpecificFilters = {
  all: [],
  image: [
    'imageCategories',
    'imageExtensions',
    'aspectRatios',
    'sizes',
    'imageProviders',
  ],
  audio: ['audioCategories', 'audioExtensions', 'durations', 'audioProviders'],
  video: [],
}

/** @type {import('./types').Filters} */
export const filterData = {
  licenses: createInitialFilters('licenses', [
    'cc0',
    'pdm',
    'by',
    'by-sa',
    'by-nc',
    'by-nd',
    'by-nc-sa',
    'by-nc-nd',
  ]),
  licenseTypes: createInitialFilters('license-types', [
    'commercial',
    'modification',
  ]),
  audioCategories: createInitialFilters('audio-categories', [
    'music',
    'sound',
    'podcast',
  ]),
  imageCategories: createInitialFilters('image-categories', [
    'photograph',
    'illustration',
    'digitized_artwork',
  ]),
  audioExtensions: createInitialFilters('audio-extensions', [
    'mp3',
    'ogg',
    'flac',
  ]),
  imageExtensions: createInitialFilters('image-extensions', [
    'jpg',
    'png',
    'gif',
    'svg',
  ]),
  aspectRatios: createInitialFilters('aspect-ratios', [
    'tall',
    'wide',
    'square',
  ]),
  durations: createInitialFilters('durations', ['short', 'medium', 'long']),
  sizes: createInitialFilters('sizes', ['small', 'medium', 'large']),
  audioProviders: [],
  imageProviders: [],
  searchBy: createInitialFilters('search-by', ['creator']),
  mature: false,
}

/**
 * Returns true if any of the filters' checked property is true
 * except for `mature` filter, as it is not displayed as a tag
 * @param filters
 * @returns {boolean}
 */
const anyFilterApplied = (filters = {}) =>
  Object.keys(filters).some((filterKey) => {
    if (filterKey === 'mature') {
      return false
    } // this is hardcoded to "false" because we do not show mature in `FilterDisplay.vue` like the other filters

    return (
      filters[filterKey] && filters[filterKey].some((filter) => filter.checked)
    )
  })

/**
 * `query` has the API request parameters for search filtering. Locally, some filters
 * have different names, and some query parameters correspond to different filter parameters
 * depending on the media type. For example, `extension` query parameter can be `audioExtension`
 * or `imageExtension`, with different values for each.
 *
 * @return {import('./types').SearchState}
 */
export const state = () => ({
  filters: clonedeep(filterData),
  searchType: IMAGE,
  query: {
    q: '',
    license: '',
    license_type: '',
    categories: '',
    extension: '',
    duration: '',
    aspect_ratio: '',
    size: '',
    source: '',
    searchBy: '',
    mature: false,
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
  /**
   * Returns all applied filters in unified format
   * Mature filter is not returned because it is not displayed
   * as a filter tag.
   *
   * @param {import('./types').SearchState} state
   * @returns {{code: string, name: string, filterType: string}[]}
   */
  appliedFilterTags: (state) => {
    let appliedFilters = []
    const filterKeys = mediaFilterKeys[state.searchType]
    filterKeys.forEach((filterType) => {
      if (filterType !== 'mature') {
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
  /**
   * Returns true if any filter except `mature` is applied.
   *
   * @param {import('./types').SearchState} state
   * @return {boolean}
   */
  isAnyFilterApplied: (state) => {
    return anyFilterApplied(
      getMediaTypeFilters({
        filters: state.filters,
        mediaType: state.searchType,
      })
    )
  },
  /**
   * Returns the array of the filters applicable for current search type
   * for display on the Filter sidebar.
   * @param {import('./types').SearchState} state
   * @return {{}}
   */
  mediaFiltersForDisplay: (state) => {
    return getMediaTypeFilters({
      filters: state.filters,
      mediaType: state.searchType,
      includeMature: false,
    })
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
      commit(CLEAR_OTHER_MEDIA_TYPE_FILTERS, { searchType })
    }
    await dispatch(UPDATE_QUERY_FROM_FILTERS, queryParams)
  },
  /**
   * Toggles a filter's checked parameter
   * @param {import('vuex').ActionContext} context
   * @param params
   */
  async [TOGGLE_FILTER]({ commit, dispatch, state }, params) {
    const { filterType, code } = params
    const filters = state.filters[filterType]
    const codeIdx = findIndex(filters, (f) => f.code === code)

    commit(SET_FILTER, { codeIdx, ...params })
    await dispatch(UPDATE_QUERY_FROM_FILTERS)
  },

  /**
   * Resets all filters to initial values.
   * Provider filters are not in the initial filters, so they need to be
   * handled separately.
   * @param {import('vuex').ActionContext} context
   */
  async [CLEAR_FILTERS]({ commit, dispatch, state }) {
    const initialFilters = clonedeep(filterData)
    const resetProviders = (mediaType) => {
      return state.filters[`${mediaType}Providers`].map((provider) => ({
        ...provider,
        checked: false,
      }))
    }
    const newFilterData = {
      ...initialFilters,
      audioProviders: resetProviders(AUDIO),
      imageProviders: resetProviders(IMAGE),
    }
    commit(REPLACE_FILTERS, { newFilterData })
    await dispatch(UPDATE_QUERY_FROM_FILTERS, { q: '' })
  },

  /**
   * Called when a /search path is server-rendered.
   * @param {import('vuex').ActionContext} context
   * @param {string} path
   * @param {Object} query
   */
  async [SET_SEARCH_STATE_FROM_URL](
    { commit, dispatch, state },
    { path, query }
  ) {
    const searchType = queryStringToSearchType(path)
    const queryParams = {}
    if (query.q) {
      queryParams.q = query.q
    }
    const newFilterData = queryToFilterData({
      query,
      searchType,
      defaultFilters: state.filters,
    })
    commit(REPLACE_FILTERS, { newFilterData })
    commit(SET_SEARCH_TYPE, { searchType })
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
      state.filters,
      params.mediaType || state.searchType,
      false
    )
    const query = { ...queryFromFilters }
    query.q = params?.q || state.query.q
    commit(SET_QUERY, { query })
  },
}

function getMediaTypeFilters({ filters, mediaType, includeMature = false }) {
  if (!supportedSearchTypes.includes(mediaType)) {
    mediaType = ALL_MEDIA
  }
  let filterKeys = mediaFilterKeys[mediaType]
  if (!includeMature) {
    filterKeys = filterKeys.filter((filterKey) => filterKey !== 'mature')
  }
  const mediaTypeFilters = {}
  filterKeys.forEach((filterKey) => {
    mediaTypeFilters[filterKey] = filters[filterKey]
  })
  return mediaTypeFilters
}

const mutations = {
  /**
   * After a search type is changed, unchecks all the filters that are not
   * applicable for this Media type.
   * @param {import('./types').SearchState} state
   * @param {import('./types').SearchType} searchType
   */
  [CLEAR_OTHER_MEDIA_TYPE_FILTERS](state, { searchType }) {
    const mediaTypesToClear = supportedSearchTypes.filter(
      (type) => type !== searchType
    )

    let filterKeysToClear = []
    mediaTypesToClear.forEach((mediaType) => {
      const filterKeys = mediaSpecificFilters[mediaType]
      filterKeysToClear = [...filterKeysToClear, ...filterKeys]
    })

    Object.keys(state.filters).forEach((filterType) => {
      if (filterKeysToClear.includes(filterType)) {
        state.filters[filterType] = state.filters[filterType].map((f) => ({
          ...f,
          checked: false,
        }))
      }
    })
  },
  /**
   * Replaces filters with the newFilterData parameter, making sure that
   * audio/image provider filters are handled correctly.
   *
   * @param {import('./types').SearchState} state
   * @param {import('./types').Filters} newFilterData
   */
  [REPLACE_FILTERS](state, { newFilterData }) {
    Object.keys(state.filters).forEach((filterType) => {
      if (filterType === 'mature') {
        state.filters.mature = newFilterData.mature
      } else if (['audioProviders', 'imageProviders'].includes(filterType)) {
        newFilterData[filterType].forEach((provider) => {
          const idx = state.filters[filterType].findIndex(
            (p) => p.code === provider.code
          )
          if (idx > -1) {
            state.filters[filterType][idx].checked = provider.checked
          }
        })
      } else {
        state.filters[filterType] = newFilterData[filterType]
      }
    })
  },
  /**
   * Toggles the filter's checked value.
   *
   * @param {import('./types').SearchState} state
   * @param {import('vuex').MutationPayload} params
   * @param {string} params.filterType
   * @param {number} params.codeIdx
   */
  [SET_FILTER](state, params) {
    const { filterType, codeIdx } = params
    if (filterType === 'mature') {
      state.filters.mature = !state.filters.mature
    } else {
      const filters = state.filters[filterType]
      filters[codeIdx].checked = !filters[codeIdx].checked
    }
  },
  [SET_PROVIDERS_FILTERS](state, params) {
    const { mediaType, providers } = params
    // merge providers from API response with the filters that came from the
    // browse URL search query string and match the checked properties
    // in the store
    const providersKey = `${mediaType}Providers`
    const currentProviders = [...state.filters[providersKey]]
    state.filters[providersKey] = providers.map((provider) => {
      const existingProviderFilterIdx = findIndex(
        currentProviders,
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
   * Sets the content type to search.
   * @param {import('./types').SearchState} state
   * @param {import('./types').SearchType} searchType
   */
  [SET_SEARCH_TYPE](state, { searchType }) {
    state.searchType = searchType
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
