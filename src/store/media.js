import findIndex from 'lodash.findindex'
import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import decodeMediaData from '~/utils/decode-media-data'
import {
  FETCH_AUDIO,
  FETCH_IMAGE,
  FETCH_MEDIA,
  FETCH_SINGLE_MEDIA_TYPE,
  HANDLE_MEDIA_ERROR,
  HANDLE_NO_MEDIA,
  CLEAR_MEDIA,
} from '~/constants/action-types'
import {
  FETCH_END_MEDIA,
  FETCH_MEDIA_ERROR,
  FETCH_START_MEDIA,
  MEDIA_NOT_FOUND,
  RESET_MEDIA,
  SET_AUDIO,
  SET_IMAGE,
  SET_MEDIA,
} from '~/constants/mutation-types'
import {
  SEND_RESULT_CLICKED_EVENT,
  SEND_SEARCH_QUERY_EVENT,
} from '~/constants/usage-data-analytics-types'
import { AUDIO, IMAGE, VIDEO, ALL_MEDIA } from '~/constants/media'
import { USAGE_DATA } from '~/constants/store-modules'
import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'

// Note: images should always be first here,
// and this only includes 'real' media. ALL is a
// special case not used in this list.
const supportedTypes = [IMAGE, AUDIO]

/**
 * @return {import('./types').MediaState}
 */
export const state = () => ({
  supportedTypes,
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

export const createActions = (services) => ({
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} [payload]
   * @return {Promise<void>}
   */
  async [FETCH_MEDIA]({ dispatch, rootState }, payload = {}) {
    const mediaType = rootState.search.query.mediaType
    const mediaToFetch = mediaType !== ALL_MEDIA ? [mediaType] : [IMAGE, AUDIO]

    await Promise.all(
      mediaToFetch.map((type) =>
        dispatch(FETCH_SINGLE_MEDIA_TYPE, { mediaType: type, ...payload })
      )
    )
  },
  // Do not use with ALL_MEDIA
  async [CLEAR_MEDIA]({ commit }, payload = {}) {
    const { mediaType } = payload
    commit(RESET_MEDIA, { mediaType })
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {Object} payload
   * @param {mediaType} payload.mediaType - the mediaType to fetch (do not use 'All_media' here)
   * @param {number} [payload.page] - API page to load.
   * @param {boolean} [payload.shouldPersistMedia] - whether the existing media
   * should be added to or replaced.
   * @return {Promise<void>}
   */
  async [FETCH_SINGLE_MEDIA_TYPE](
    { commit, dispatch, rootState, rootGetters },
    payload
  ) {
    const {
      mediaType,
      page = undefined,
      shouldPersistMedia = false,
      ...params
    } = payload

    const queryParams = prepareSearchQueryParams({
      ...rootGetters['search/searchQueryParams'],
      ...params,
    })

    // does not send event if user is paginating for more results
    if (!page) {
      const sessionId = rootState.user.usageSessionId
      await dispatch(
        `${USAGE_DATA}/${SEND_SEARCH_QUERY_EVENT}`,
        { query: queryParams.q, sessionId },
        { root: true }
      )
    }

    commit(FETCH_START_MEDIA, { mediaType })
    try {
      const mediaPage = typeof page === 'undefined' ? page : page[mediaType]

      const res = await services[mediaType].search({
        ...queryParams,
        page: mediaPage,
      })

      commit(FETCH_END_MEDIA, { mediaType })
      const data = services[mediaType].transformResults(res.data)
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
   * @param params
   * @return {Promise<void>}
   */
  async [FETCH_AUDIO]({ commit, dispatch, state, rootState }, params) {
    await dispatch(
      `${USAGE_DATA}/${SEND_RESULT_CLICKED_EVENT}`,
      {
        query: rootState.search.query.q,
        resultUuid: params.id,
        resultRank: findIndex(
          state.results.audio.items,
          (item) => item.id === params.id
        ),
        sessionId: rootState.user.usageSessionId,
      },
      { root: true }
    )
    commit(SET_AUDIO, { audio: {} })
    await services[AUDIO].getMediaDetail(params)
      .then(({ data }) => {
        commit(SET_AUDIO, { audio: data })
      })
      .catch((error) => {
        if (error.response && error.response.status === 404) {
          commit(MEDIA_NOT_FOUND, { mediaType: AUDIO })
        } else {
          dispatch(HANDLE_MEDIA_ERROR, { mediaType: AUDIO, error })
        }
      })
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param params
   * @return {Promise<void>}
   */
  async [FETCH_IMAGE]({ commit, dispatch, state, rootState }, params) {
    await dispatch(
      `${USAGE_DATA}/${SEND_RESULT_CLICKED_EVENT}`,
      {
        query: rootState.search.query.q,
        resultUuid: params.id,
        resultRank: findIndex(
          state.results.image.items,
          (img) => img.id === params.id
        ),
        sessionId: rootState.user.usageSessionId,
      },
      { root: true }
    )

    commit(SET_IMAGE, { image: {} })
    await services[IMAGE].getMediaDetail(params)
      .then(({ data }) => {
        commit(SET_IMAGE, { image: data })
      })
      .catch((error) => {
        if (error.response && error.response.status === 404) {
          commit(MEDIA_NOT_FOUND, { mediaType: IMAGE })
        } else {
          throw new Error(`Error fetching the image: ${error.message}`)
        }
      })
  },
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param {object} payload
   * @param {mediaType} payload.mediaType
   * @param payload.error
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
   * @param {'audio'|'image'} mediaType
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

export const getters = {
  /**
   * Returns the search result data related for selected media.
   * @param {import('./types').MediaState} state
   * @param getters
   * @return {import('./types').MediaStoreResult[] | {'audio': import('./types').MediaStoreResult, 'image': import('./types').MediaStoreResult}}
   */
  results(state, getters) {
    if (getters.searchType === ALL_MEDIA) {
      return { [IMAGE]: state.results[IMAGE], [AUDIO]: state.results[AUDIO] }
    } else {
      return getters.mediaType
        ? { [getters.mediaType]: state.results[getters.mediaType] }
        : {}
    }
  },
  mediaResults(state, getters) {
    if (getters.searchType === ALL_MEDIA) {
      return {
        [IMAGE]: state.results[IMAGE].items,
        [AUDIO]: state.results[AUDIO].items,
      }
    } else {
      return {
        [getters.mediaType]: state.results[getters.mediaType].items ?? {},
      }
    }
  },
  resultCount(state, getters) {
    if (getters.searchType === ALL_MEDIA) {
      /**
       * API returns 10 000 if there are more than 10 000 results,
       * Count for all media also returns at most 10 000.
       */
      const count = supportedTypes
        .map((type) => state.results[type].count)
        .reduce((a, b) => a + b, 0)
      return count > 10000 ? 10000 : count
    } else {
      return state.results[getters.searchType]?.count || 0
    }
  },
  /**
   * Search fetching state for selected media type.
   * @param {import('./types').MediaState} state
   * @param getters
   * @returns {import('./types').fetchState}
   */
  fetchState(state, getters) {
    if (getters.searchType === ALL_MEDIA) {
      return {
        isFetching:
          state.fetchState[AUDIO].isFetching ||
          state.fetchState[IMAGE].isFetching,
        fetchError:
          state.fetchState[AUDIO].fetchError ||
          state.fetchState[IMAGE].fetchError,
        isFinished:
          state.fetchState[AUDIO].isFinished &&
          state.fetchState[IMAGE].isFinished,
      }
    } else {
      return (
        state.fetchState[getters.mediaType] || {
          isFetching: false,
          fetchError: false,
          isFinished: true,
        }
      )
    }
  },
  searchType(state, getters, rootState) {
    return rootState.search.searchType
  },
  mediaType(state, getters, rootState) {
    return rootState.search.query.mediaType
  },
  /**
   * Returns true for media types that are not supported in the API: video and currently audio.
   *
   * @param state
   * @param getters
   * @param rootState
   * @returns {boolean}
   */
  unsupportedMediaType(state, getters, rootState) {
    const mediaType = rootState.search.searchType
    return mediaType === VIDEO
  },
}

export const mutations = {
  /**
   * Sets the fetchState for all passed mediaTypes at the beginning of fetching.
   * @param _state
   * @param {MediaType} mediaTypes
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
   * @param {MediaType} params.mediaType
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
  [SET_AUDIO](_state, params) {
    _state.audio = decodeMediaData(params.audio, AUDIO)
  },
  [SET_IMAGE](_state, params) {
    _state.image = decodeMediaData(params.image)
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
    _state.results[mediaType].items = mediaToSet
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
   * @param {MediaType} mediaTypes
   */
  [RESET_MEDIA](_state, { mediaType }) {
    _state.results[mediaType].items = {}
    _state.results[mediaType].count = 0
    _state.results[mediaType].page = undefined
    _state.results[mediaType].pageCount = 0
  },
}

const mediaServices = { [AUDIO]: AudioService, [IMAGE]: ImageService }
const actions = createActions(mediaServices)

export default {
  state,
  getters,
  actions,
  mutations,
}
