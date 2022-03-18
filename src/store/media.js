import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import {
  FETCH_MEDIA,
  FETCH_SINGLE_MEDIA_TYPE,
  HANDLE_MEDIA_ERROR,
  HANDLE_NO_MEDIA,
  CLEAR_MEDIA,
  FETCH_MEDIA_ITEM,
} from '~/constants/action-types'
import {
  FETCH_END_MEDIA,
  FETCH_MEDIA_ERROR,
  FETCH_START_MEDIA,
  MEDIA_NOT_FOUND,
  RESET_MEDIA,
  SET_MEDIA_ITEM,
  SET_MEDIA,
  RESET_FETCH_STATE,
} from '~/constants/mutation-types'
import { AUDIO, IMAGE, ALL_MEDIA, supportedMediaTypes } from '~/constants/media'
import MediaService from '~/data/media-service'

import { hash, rand as prng } from '~/utils/prng'

/**
 * @return {import('./types').MediaState}
 */
export const state = () => ({
  results: {
    [IMAGE]: {
      count: 0,
      page: undefined,
      pageCount: 0,
      items: {},
    },
    [AUDIO]: {
      count: 0,
      page: undefined,
      pageCount: 0,
      items: {},
    },
  },
  fetchState: {
    audio: {
      isFetching: false,
      fetchingError: null,
      isFinished: false,
    },
    image: {
      isFetching: false,
      fetchingError: null,
      isFinished: false,
    },
  },
  audio: {},
  image: {},
})

export const mediaServices = {
  [AUDIO]: new MediaService(AUDIO),
  [IMAGE]: new MediaService(IMAGE),
}

export const createActions = (services = mediaServices) => ({
  /**
   * Calls FETCH_SINGLE_MEDIA_TYPE for selected media type(s). Can be called by changing the search query
   * (search term or filter item), or by clicking 'Load more' button.
   * If the search query changed, fetch state is reset, otherwise only the media types for which
   * fetchState.isFinished is not true are fetched.
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} [payload]
   * @param {boolean} [payload.shouldPersistMedia] - true when fetching more media for the same query.
   * @return {Promise<void>}
   */
  async [FETCH_MEDIA]({ commit, dispatch, getters, state }, payload = {}) {
    const mediaType = getters.searchType
    if (!payload.shouldPersistMedia) {
      commit(RESET_FETCH_STATE)
    }
    const mediaToFetch = (
      mediaType !== ALL_MEDIA ? [mediaType] : [IMAGE, AUDIO]
    ).filter((type) => !state.fetchState[type].isFinished)

    await Promise.all(
      mediaToFetch.map((type) =>
        dispatch(FETCH_SINGLE_MEDIA_TYPE, { mediaType: type, ...payload })
      )
    )
  },
  /**
   * Do not use with ALL_MEDIA
   * @param {import('vuex').ActionContext} context
   * @param {object} payload
   * @param {import('./types').SupportedMediaType} payload.mediaType
   * @returns {Promise<void>}
   */
  async [CLEAR_MEDIA]({ commit }, payload = {}) {
    const { mediaType } = payload
    commit(RESET_MEDIA, { mediaType })
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} payload
   * @param {import('./types').SupportedMediaType} payload.mediaType - the mediaType to fetch (do not use 'All_media' here)
   * @param {number} [payload.page] - API page to load.
   * @param {boolean} [payload.shouldPersistMedia] - whether the existing media should be added to or replaced.
   * @return {Promise<void>}
   */
  async [FETCH_SINGLE_MEDIA_TYPE](
    { commit, dispatch, rootGetters, state },
    payload
  ) {
    const { mediaType, shouldPersistMedia = false, ...params } = payload

    const queryParams = prepareSearchQueryParams({
      ...rootGetters['search/searchQueryParams'],
      ...params,
    })

    commit(FETCH_START_MEDIA, { mediaType })
    try {
      let mediaPage
      if (shouldPersistMedia) {
        mediaPage = state.results[mediaType].page + 1
      }
      const data = await services[mediaType].search({
        ...queryParams,
        page: mediaPage,
      })

      commit(FETCH_END_MEDIA, { mediaType })
      const mediaCount = data.result_count
      commit(SET_MEDIA, {
        mediaType,
        media: data.results,
        mediaCount,
        pageCount: data.page_count,
        shouldPersistMedia,
        page: mediaPage,
      })
      await dispatch(HANDLE_NO_MEDIA, {
        mediaType,
        mediaCount,
      })
    } catch (error) {
      await dispatch(HANDLE_MEDIA_ERROR, { mediaType, error })
    }
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} params
   * @param {import('../constants/media').MediaType} params.mediaType
   * @param {string} params.id
   * @return {Promise<void>}
   */
  async [FETCH_MEDIA_ITEM]({ commit, dispatch }, params) {
    const { mediaType } = params
    try {
      const data = await services[mediaType].getMediaDetail(params)
      commit(SET_MEDIA_ITEM, { item: data, mediaType })
    } catch (error) {
      commit(SET_MEDIA_ITEM, { item: {}, mediaType })
      if (error.response && error.response.status === 404) {
        commit(MEDIA_NOT_FOUND, { mediaType })
      } else {
        await dispatch(HANDLE_MEDIA_ERROR, { mediaType, error })
      }
    }
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} payload
   * @param {import('./types').SupportedMediaType} payload.mediaType
   * @param {unknown} payload.error
   * @return {Promise<void>}
   */
  async [HANDLE_MEDIA_ERROR]({ commit }, { mediaType, error }) {
    let errorMessage
    if (error.response) {
      errorMessage =
        error.response.status === 500
          ? 'There was a problem with our servers'
          : error.response.message
      commit(FETCH_MEDIA_ERROR, { mediaType, errorMessage })
    } else {
      commit(FETCH_MEDIA_ERROR, { mediaType, errorMessage: error.message })
      throw new Error(error)
    }
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {number} mediaCount
   * @param {import('./types').SupportedMediaType} mediaType
   */
  [HANDLE_NO_MEDIA]({ commit }, { mediaCount, mediaType }) {
    if (!mediaCount) {
      commit(FETCH_MEDIA_ERROR, {
        mediaType,
        errorMessage: `No ${mediaType} found for this query`,
      })
    }
  },
})
const actions = createActions()

export const getters = {
  getItemById: (state) => (mediaType, id) => {
    return state.results[mediaType].items[id]
  },
  /**
   * Returns object with a key for each supported media type and arrays of media items for each.
   * @param {import('./types').MediaState} state
   * @returns {{[p: import('./types').MediaType]: import('./types').MediaDetail[]}}
   */
  resultItems(state) {
    return supportedMediaTypes.reduce(
      (items, type) => ({
        ...items,
        [type]: Object.values(state.results[type].items),
      }),
      /** @type{{ [key: import('./types').MediaType]: import('./types').MediaDetail[] }} */ ({})
    )
  },
  /**
   * Returns result item counts for each supported media type.
   * @param {import('./types').MediaState} state
   * @returns {[import('./types').MediaType, number][]}
   */
  resultCountsPerMediaType(state) {
    return supportedMediaTypes.map((type) => [type, state.results[type].count])
  },
  /**
   * Returns the total count of results for selected search type, sums all media results for ALL_MEDIA.
   * If the count is more than 10000, returns 10000 to match the API result.
   * @param {import('./types').MediaState} state
   * @param getters
   * @returns {number}
   */
  resultCount(state, getters) {
    const count = (
      getters.searchType === ALL_MEDIA
        ? supportedMediaTypes
        : [getters.searchType]
    ).reduce((sum, mediaType) => sum + state.results[mediaType].count, 0)
    return Math.min(count, 10000)
  },
  /**
   * Search fetching state for selected media type.
   * @param {import('./types').MediaState} state
   * @param getters
   * @returns {import('./types').fetchState}
   */
  fetchState(state, getters) {
    if (getters.searchType === ALL_MEDIA) {
      /**
       * For all_media, we return the error for the first media type that has an error.
       */
      const mediaTypeErrors = supportedMediaTypes.filter(
        (type) => !!state.fetchState[type].fetchingError
      )
      const allContentFetchError = mediaTypeErrors.length
        ? mediaTypeErrors[0]
        : null

      return {
        isFetching:
          supportedMediaTypes.filter(
            (type) => state.fetchState[type].isFetching
          ).length > 0,
        fetchError: allContentFetchError,
        isFinished:
          supportedMediaTypes.filter(
            (type) => state.fetchState[type].isFinished
          ).length === supportedMediaTypes.length,
      }
    } else {
      return (
        state.fetchState[getters.searchType] || {
          isFetching: false,
          fetchError: false,
          isFinished: true,
        }
      )
    }
  },
  allMedia(state, getters) {
    const media = getters.resultItems

    // Seed the random number generator with the ID of
    // the first search result, so the non-image
    // distribution is the same on repeated searches
    let seed = media[IMAGE][0]?.id
    if (typeof seed === 'string') {
      seed = hash(seed)
    }
    const rand = prng(seed)
    const randomIntegerInRange = (min, max) =>
      Math.floor(rand() * (max - min + 1)) + min
    /**
     * When navigating from All page to Audio page, VAllResultsGrid is displayed
     * for a short period of time. Then media['image'] is undefined, and it throws an error
     * `TypeError: can't convert undefined to object`. To fix it, we add `|| {}` to the media['image'].
     */
    /**
     * First, set the results to all images
     * @type {import('./types').MediaDetail[]}
     */
    const newResults = media.image

    // push other items into the list, using a random index.
    let nonImageIndex = 1
    for (const type of supportedMediaTypes.slice(1)) {
      for (const item of media[type]) {
        newResults.splice(nonImageIndex, 0, item)
        if (nonImageIndex > newResults.length + 1) break
        nonImageIndex = randomIntegerInRange(
          nonImageIndex + 1,
          nonImageIndex + 6
        )
      }
    }

    return newResults
  },
  searchType(state, getters, rootState) {
    return rootState.search.searchType
  },
}

export const mutations = {
  /**
   * Sets the fetchState for all passed mediaTypes at the beginning of fetching.
   * @param _state
   * @param {import('./types').MediaType} mediaType
   */
  [FETCH_START_MEDIA](_state, { mediaType }) {
    _state.fetchState[mediaType].isFetching = true
    _state.fetchState[mediaType].fetchingError = null
    _state.fetchState[mediaType].isFinished = false
  },
  /**
   * Sets the fetchState.isFetching to false for all passed mediaTypes at the end of fetching.
   * @param _state
   * @param {object} params
   * @param {import('./types').MediaType} params.mediaType
   */
  [FETCH_END_MEDIA](_state, { mediaType }) {
    _state.fetchState[mediaType].isFetching = false
  },
  [FETCH_MEDIA_ERROR](_state, params) {
    const { mediaType, errorMessage } = params
    _state.fetchState[mediaType].isFetching = false
    _state.fetchState[mediaType].fetchingError = errorMessage
    _state.fetchState[mediaType].isFinished = true
  },
  [SET_MEDIA_ITEM](_state, params) {
    const { item, mediaType } = params
    _state[mediaType] = item
  },
  [SET_MEDIA](_state, params) {
    const {
      mediaType,
      media,
      mediaCount,
      page,
      pageCount,
      shouldPersistMedia,
    } = params
    let mediaToSet
    if (shouldPersistMedia) {
      mediaToSet = { ..._state.results[mediaType].items, ...media }
    } else {
      mediaToSet = media
    }
    const mediaPage = page || 1
    _state.results[mediaType].items = Object.freeze(mediaToSet)
    _state.results[mediaType].count = mediaCount || 0
    _state.results[mediaType].page = mediaPage
    _state.results[mediaType].pageCount = pageCount
    _state.fetchState[mediaType].isFinished = mediaPage >= pageCount
  },
  [MEDIA_NOT_FOUND](_state, params) {
    throw new Error(`Media of type ${params.mediaType} not found`)
  },
  /**
   * Clears the items for all passed media types, and resets fetch state.
   * @param _state
   * @param {import('./types').MediaType} mediaType
   */
  [RESET_MEDIA](_state, { mediaType }) {
    _state.results[mediaType].items = {}
    _state.results[mediaType].count = 0
    _state.results[mediaType].page = undefined
    _state.results[mediaType].pageCount = 0
  },
  [RESET_FETCH_STATE](_state) {
    for (let mediaType of supportedMediaTypes) {
      _state.fetchState[mediaType].isFetching = false
      _state.fetchState[mediaType].isFinished = false
      _state.fetchState[mediaType].fetchingError = null
    }
  },
}

export default {
  state,
  getters,
  actions,
  mutations,
}
