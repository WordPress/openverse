import findIndex from 'lodash.findindex'
import clonedeep from 'lodash.clonedeep'

import local from '~/utils/local'
import {
  filtersToQueryData,
  queryToFilterData,
} from '~/utils/searchQueryTransform'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  VIDEO,
  supportedMediaTypes,
} from '~/constants/media'
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_FILTERS,
  SET_FILTERS_FROM_URL,
  SET_FILTER_IS_VISIBLE,
  UPDATE_FILTERS,
} from '~/store-modules/mutation-types'

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
  audio: [
    'licenses',
    'licenseTypes',
    'audioCategories',
    'audioExtensions',
    'durations',
    'audioProviders',
    'searchBy',
    'mature',
  ],
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
  audio: ['audioCategories', 'audioExtensions', 'durations', 'audioProviders'],
  video: [],
}

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

/**
 * Returns true if any of the filters' checked property is true
 * except for `mature` filter, as it is not displayed as a tag
 * @param filters
 * @returns {boolean}
 */
const anyFilterApplied = (filters) =>
  Object.keys(filters).some((filterKey) => {
    if (filterKey === 'mature') {
      return false
    } // this is hardcoded to "false" because we do not show mature in `FilterDisplay.vue` like the other filters

    return filters[filterKey].some((filter) => filter.checked)
  })

const state = {
  filters: filterData,
  isFilterVisible: false,
}

const getters = {
  /**
   * Returns all applied filters in unified format
   * Mature filter is not returned because it is not displayed
   * as a filter tag
   * @param state
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
  isAnyFilterApplied: (state) => {
    return anyFilterApplied(
      getMediaTypeFilters(state, { mediaType: state.searchType })
    )
  },
  allFiltersForDisplay: (state) => {
    return getMediaTypeFilters(state, {
      mediaType: ALL_MEDIA,
      includeMature: false,
    })
  },
  audioFiltersForDisplay: (state) => {
    return getMediaTypeFilters(state, {
      mediaType: AUDIO,
      includeMature: false,
    })
  },
  imageFiltersForDisplay: (state) => {
    return getMediaTypeFilters(state, {
      mediaType: IMAGE,
      includeMature: false,
    })
  },
  videoFiltersForDisplay: (state) => {
    return getMediaTypeFilters(state, {
      mediaType: VIDEO,
      includeMature: false,
    })
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
  const query = filtersToQueryData(state.filters, state.searchType)

  state.query = {
    q: state.query.q,
    ...query,
  }
}

function getMediaTypeFilters(state, { mediaType, includeMature = false }) {
  let filterKeys = mediaFilterKeys[mediaType]
  if (!includeMature) {
    filterKeys = filterKeys.filter((filterKey) => filterKey !== 'mature')
  }
  const mediaTypeFilters = {}
  filterKeys.forEach((filterKey) => {
    mediaTypeFilters[filterKey] = state.filters[filterKey]
  })
  return mediaTypeFilters
}

function replaceFilters(state, filterData) {
  Object.keys(state.filters).forEach((filterType) => {
    if (filterType === 'mature') {
      state.filters.mature = filterData.mature
    } else if (['audioProviders', 'imageProviders'].includes(filterType)) {
      filterData[filterType].forEach((provider) => {
        const idx = state.filters[filterType].findIndex(
          (p) => p.code === provider.code
        )
        if (idx > -1) {
          state.filters[filterType][idx].checked = provider.checked
        }
      })
    } else {
      state.filters[filterType] = filterData[filterType]
    }
  })
}

function setFilter(state, params) {
  const { filterType, codeIdx } = params
  if (filterType === 'mature') {
    state.filters.mature = !state.filters.mature
  } else {
    const filters = state.filters[filterType]
    filters[codeIdx].checked = !filters[codeIdx].checked
  }

  setQuery(state, params)
}

// Make sure when redirecting after applying a filter, we stick to the right tab (i.e, "/search/video", "/search/audio", etc.)
const mutations = {
  [UPDATE_FILTERS](state) {
    const mediaTypesToClear = supportedMediaTypes.filter(
      (media) => media !== state.searchType
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
  [SET_FILTERS_FROM_URL](state, params) {
    replaceFilters(state, queryToFilterData(params.url))
  },
  [SET_FILTER](state, params) {
    return setFilter(state, params)
  },
  [CLEAR_FILTERS](state) {
    const initialFilters = clonedeep(filterData)

    const resetProviders = (mediaType) => {
      return state.filters[`${mediaType}Providers`].map((provider) => ({
        ...provider,
        checked: false,
      }))
    }
    state.filters = {
      ...initialFilters,
      audioProviders: resetProviders(AUDIO),
      imageProviders: resetProviders(IMAGE),
    }
    return setQuery(state)
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
}

export default {
  state,
  getters,
  actions,
  mutations,
}
