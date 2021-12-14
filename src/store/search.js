import findIndex from 'lodash.findindex'
import clonedeep from 'lodash.clonedeep'

import local from '~/utils/local'
import {
  filtersToQueryData,
  queryStringToSearchType,
  queryToFilterData,
} from '~/utils/search-query-transform'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  supportedMediaTypes,
  VIDEO,
} from '~/constants/media'
import {
  UPDATE_QUERY,
  SET_MEDIA_TYPE,
  SET_SEARCH_STATE_FROM_URL,
  TOGGLE_FILTER,
  UPDATE_QUERY_FROM_FILTERS,
  UPDATE_SEARCH_TYPE,
  CLEAR_FILTERS,
} from '~/constants/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  SET_FILTER_IS_VISIBLE,
  CLEAR_OTHER_MEDIA_TYPE_FILTERS,
  REPLACE_FILTERS,
  SET_QUERY,
  SET_SEARCH_TYPE,
} from '~/constants/mutation-types'

// The order of the keys here is the same as in the side filter display
export const mediaFilterKeys = {
  image: [
    'licenses',
    'licenseTypes',
    'imageCategories',
    'imageExtensions',
    'aspectRatios',
    'sizes',
    'imageProviders',
    'searchBy',
    'mature',
  ],
  audio: process.env.enableAudio
    ? [
        'licenses',
        'licenseTypes',
        'audioCategories',
        'audioExtensions',
        'durations',
        'audioProviders',
        'searchBy',
        'mature',
      ]
    : [],
  video: [],
  all: ['licenses', 'licenseTypes', 'searchBy', 'mature'],
}

export const mediaSpecificFilters = {
  all: ['licenses', 'licenseTypes', 'searchBy', 'mature'],
  image: [
    'imageCategories',
    'imageExtensions',
    'aspectRatios',
    'sizes',
    'imageProviders',
  ],
  audio: process.env.enableAudio
    ? ['audioCategories', 'audioExtensions', 'durations', 'audioProviders']
    : [],
  video: [],
}

/** @type {import('./types').Filters} */
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
  audioCategories: [
    {
      code: 'music',
      name: 'filters.audio-categories.music',
      checked: false,
    },
    {
      code: 'soundEffects',
      name: 'filters.audio-categories.sound-effects',
      checked: false,
    },
    {
      code: 'podcast',
      name: 'filters.audio-categories.podcast',
      checked: false,
    },
  ],
  imageCategories: [
    {
      code: 'photograph',
      name: 'filters.image-categories.photograph',
      checked: false,
    },
    {
      code: 'illustration',
      name: 'filters.image-categories.illustration',
      checked: false,
    },
    {
      code: 'digitized_artwork',
      name: 'filters.image-categories.digitized-artwork',
      checked: false,
    },
  ],
  audioExtensions: [
    { code: 'mp3', name: 'filters.audio-extensions.mp3', checked: false },
    { code: 'ogg', name: 'filters.audio-extensions.ogg', checked: false },
    { code: 'flac', name: 'filters.audio-extensions.flac', checked: false },
  ],
  imageExtensions: [
    { code: 'jpg', name: 'filters.image-extensions.jpg', checked: false },
    { code: 'png', name: 'filters.image-extensions.png', checked: false },
    { code: 'gif', name: 'filters.image-extensions.gif', checked: false },
    { code: 'svg', name: 'filters.image-extensions.svg', checked: false },
  ],
  aspectRatios: [
    { code: 'tall', name: 'filters.aspect-ratios.tall', checked: false },
    { code: 'wide', name: 'filters.aspect-ratios.wide', checked: false },
    { code: 'square', name: 'filters.aspect-ratios.square', checked: false },
  ],
  durations: [
    { code: 'short', name: 'filters.durations.short', checked: false },
    { code: 'medium', name: 'filters.durations.medium', checked: false },
    { code: 'long', name: 'filters.durations.long', checked: false },
  ],
  sizes: [
    { code: 'small', name: 'filters.sizes.small', checked: false },
    { code: 'medium', name: 'filters.sizes.medium', checked: false },
    { code: 'large', name: 'filters.sizes.large', checked: false },
  ],
  audioProviders: [],
  imageProviders: [],
  searchBy: [
    { code: 'creator', name: 'filters.searchBy.creator', checked: false },
  ],
  mature: false,
}
const supportedTabTypes = [AUDIO, IMAGE]
if (process.env.enableAudio) {
  supportedTabTypes.unshift(ALL_MEDIA)
}
const searchTabToMediaType = process.env.enableAudio
  ? {
      [ALL_MEDIA]: IMAGE,
      [AUDIO]: AUDIO,
      [IMAGE]: IMAGE,
      [VIDEO]: null,
    }
  : {
      [ALL_MEDIA]: IMAGE,
      [AUDIO]: null,
      [IMAGE]: IMAGE,
      [VIDEO]: null,
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
 * Search type is the media tab that is currently open in the UI. Some types
 * are not supported by the API (video), or default to a different type (all - image).
 * The media type that is actually queried is saved as `query.mediaType`, and can
 * be null for unsupported type.
 * `query` has the API request parameters for search filtering. Locally, some filters
 * have different names, and some query parameters correspond to different filter parameters
 * depending on the media type. For example, `extension` query parameter can be `audioExtension`
 * or `imageExtension`, with different values for each.
 *
 * @return {import('./types').SearchState}
 */
export const state = () => ({
  filters: clonedeep(filterData),
  isFilterVisible: false,
  searchType: IMAGE,
  query: {
    q: '',
    mediaType: IMAGE,
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
   * drops `mediaType` parameter, and all parameters with blank values.
   * @param {import('./types').SearchState} state
   * @return {import('./types').ApiQueryParams}
   */
  searchQueryParams: (state) => {
    const params = {}
    // Ensure that q filter always comes first
    if (state.query.q.trim() !== '') {
      params.q = state.query.q.trim()
    }
    // Remove the mediaType parameter, and handle mature filter separately
    const filterKeys = Object.keys(state.query).filter(
      (key) => !['q', 'mediaType', 'mature'].includes(key)
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
    if (state.query.mediaType) {
      const filterKeys = mediaFilterKeys[state.query.mediaType]
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
    }
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
        mediaType: state.query.mediaType,
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
      mediaType: state.query.mediaType,
      includeMature: false,
    })
  },
}

const actions = {
  /**
   * Called when `q` search term or `searchType` (ie. the search tab in the UI)
   * are changed.
   * We avoid adding changes to `q` or `searchType` separately, because every
   * change to the state `query` object causes an API call.
   * @param {import('vuex').ActionContext} context
   * @param {import('vuex').ActionPayload} params
   * @param {string} [params.q]
   * @param {('all'|'audio'|'image'|'video')} [params.searchType]
   * @return {Promise<void>}
   */
  async [UPDATE_QUERY]({ commit, dispatch, state }, params = {}) {
    const { q, searchType } = params
    /** @type {{ q: string?, mediaType: string? }} */
    const queryParams = {}
    if (q) {
      queryParams.q = q.trim()
    }
    if (searchType && searchType !== state.searchType) {
      commit(SET_SEARCH_TYPE, { searchType })
      const newMediaType = searchTabToMediaType[searchType]
      if (newMediaType !== state.query.mediaType) {
        queryParams.mediaType = newMediaType
      }
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
    const mediaType = searchTabToMediaType[searchType]
    const queryParams = { mediaType }
    if (query.q) {
      queryParams.q = query.q
    }
    const newFilterData = queryToFilterData({
      query,
      searchType,
      defaultFilters: state.filters,
    })
    commit(REPLACE_FILTERS, { newFilterData })
    commit(SET_SEARCH_TYPE, { searchType: searchType })
    await dispatch(UPDATE_QUERY_FROM_FILTERS, queryParams)
  },

  /**
   * On selecting a search tab, updates the search type and
   * sets the filters that are applicable for this media type.
   * @param {import('vuex').ActionContext} context
   * @param {'all'|'audio'|'image'|'video'} searchType
   */
  async [UPDATE_SEARCH_TYPE]({ commit, state }, { searchType }) {
    if (state.searchType !== searchType) {
      commit(SET_SEARCH_TYPE, { searchType })
      commit(CLEAR_OTHER_MEDIA_TYPE_FILTERS, { searchType })

      const newMediaType = searchTabToMediaType[searchType]
      if (state.query.mediaType !== newMediaType) {
        commit(SET_MEDIA_TYPE, { mediaType: newMediaType })
      }
    }
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
      params.mediaType || state.query.mediaType,
      false
    )
    const query = { ...queryFromFilters }
    query.q = params?.q || state.query.q
    query.mediaType = params?.mediaType || state.query.mediaType

    commit(SET_QUERY, { query })
  },
}

function getMediaTypeFilters({ filters, mediaType, includeMature = false }) {
  if (![ALL_MEDIA, AUDIO, IMAGE, VIDEO].includes(mediaType)) {
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

// Make sure when redirecting after applying a filter, we stick to the right tab (i.e, "/search/video", "/search/audio", etc.)
const mutations = {
  /**
   * After a search type is changed, unchecks all the filters that are not
   * applicable for this Media type.
   * @param {import('./types').SearchState} state
   * @param {'all'|'audio'|'image'|'video'} searchType
   */
  [CLEAR_OTHER_MEDIA_TYPE_FILTERS](state, { searchType }) {
    const mediaTypesToClear = supportedMediaTypes.filter(
      (media) => media !== searchType
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
  [SET_FILTER_IS_VISIBLE](state, params) {
    state.isFilterVisible = params.isFilterVisible
    local.set(process.env.filterStorageKey, params.isFilterVisible)
  },
  /**
   * Sets the searchType (tab in the UI).
   * @param {import('./types').SearchState} state
   * @param {'all'|'image'|'audio'|'video'} searchType
   */
  [SET_SEARCH_TYPE](state, { searchType }) {
    state.searchType = searchType
  },
  /**
   * Sets the query mediaType: the actual media type that is used in the API call.
   * @param {import('./types').SearchState} state
   * @param {'image'|'audio'} mediaType
   */
  [SET_MEDIA_TYPE](state, { mediaType }) {
    state.query.mediaType = mediaType
  },
  /**
   * Replaces the query object that is used for API calls.
   * @param {import('./types').SearchState} state
   * @param {Object} query
   */
  [SET_QUERY](state, { query }) {
    if (!query.mediaType) {
      query = {
        ...query,
        mediaType: state.query.mediaType,
      }
    }
    state.query = query
  },
}

export default {
  state,
  getters,
  actions,
  mutations,
}
