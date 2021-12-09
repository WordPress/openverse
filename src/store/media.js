import findIndex from 'lodash.findindex'
import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import decodeMediaData from '~/utils/decode-media-data'
import {
  FETCH_AUDIO,
  FETCH_IMAGE,
  FETCH_MEDIA,
  HANDLE_MEDIA_ERROR,
  HANDLE_NO_MEDIA,
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
import { AUDIO, IMAGE } from '~/constants/media'
import { USAGE_DATA } from '~/constants/store-modules'
import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'

/**
 * @return {import('./types').MediaState}
 */
export const state = () => ({
  results: {
    audio: {
      count: 0,
      page: undefined,
      pageCount: 0,
      items: {},
    },
    image: {
      count: 0,
      page: undefined,
      pageCount: 0,
      items: {},
    },
  },
  fetchingState: {
    audio: {
      isFetching: false,
      fetchingError: null,
    },
    image: {
      isFetching: false,
      fetchingError: null,
    },
  },
  audio: {},
  image: {},
})

export const createActions = (services) => ({
  /**
   *
   * @param {import('vuex').ActionContext} context
   * @param params
   * @return {Promise<void>}
   */
  async [FETCH_MEDIA]({ commit, dispatch, rootState, rootGetters }, params) {
    // does not send event if user is paginating for more results
    const { page, mediaType, q } = params
    const sessionId = rootState.user.usageSessionId
    if (!page) {
      await dispatch(
        `${USAGE_DATA}/${SEND_SEARCH_QUERY_EVENT}`,
        { query: q, sessionId },
        { root: true }
      )
    }

    commit(FETCH_START_MEDIA, { mediaType })
    if (!params.page) {
      commit(RESET_MEDIA, { mediaType })
    }
    const queryParams = prepareSearchQueryParams({
      ...rootGetters['search/searchQueryParams'],
      ...params,
    })
    if (!Object.keys(services).includes(mediaType)) {
      throw new Error(`Cannot fetch unknown media type "${mediaType}"`)
    }
    await services[mediaType]
      .search(queryParams)
      .then(({ data }) => {
        commit(FETCH_END_MEDIA, { mediaType })
        return data
      })
      .then(services[mediaType].transformResults)
      .then((data) => {
        const mediaCount = data.result_count
        commit(SET_MEDIA, {
          mediaType,
          media: data.results,
          mediaCount,
          pageCount: data.page_count,
          shouldPersistMedia: params.shouldPersistMedia,
          page: page,
        })
        dispatch(HANDLE_NO_MEDIA, { mediaType, mediaCount })
      })
      .catch((error) => {
        dispatch(HANDLE_MEDIA_ERROR, { mediaType, error })
      })
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
   * @param {'audio'|'image'} mediaType
   * @param error
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
   * @param rootState
   * @return {import('./types').MediaStoreResult}
   */
  results(state, getters, rootState) {
    return state.results[rootState.search.query.mediaType]
  },
  /**
   * Search fetching state for selected media type.
   * @param {import('./types').MediaState} state
   * @param getters
   * @param rootState
   * @returns {import('./types').FetchingState}
   */
  fetchingState(state, getters, rootState) {
    return state.fetchingState[rootState.search.query.mediaType]
  },
  /**
   * Returns true if all pages from the search result have been shown.
   * @param {import('./types').MediaState} state
   * @param getters
   * @param rootState
   * @returns {boolean}
   */
  isFinished(state, getters, rootState) {
    return (
      state.results[rootState.search.query.mediaType].page >=
      state.results[rootState.search.query.mediaType].pageCount
    )
  },
}

export const mutations = {
  [FETCH_START_MEDIA](_state, { mediaType }) {
    _state.fetchingState[mediaType].isFetching = true
    _state.fetchingState[mediaType].fetchingError = null
  },
  [FETCH_END_MEDIA](_state, { mediaType }) {
    _state.fetchingState[mediaType].isFetching = false
  },
  [FETCH_MEDIA_ERROR](_state, params) {
    const { mediaType, errorMessage } = params
    _state.fetchingState[mediaType].isFetching = false
    _state.fetchingState[mediaType].fetchingError = errorMessage
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
    _state.results[mediaType].items = mediaToSet
    _state.results[mediaType].count = mediaCount || 0
    _state.results[mediaType].page = page || 1
    _state.results[mediaType].pageCount = pageCount
  },
  [MEDIA_NOT_FOUND](_state, params) {
    throw new Error(`Media of type ${params.mediaType} not found`)
  },
  [RESET_MEDIA](_state, params) {
    let mediaTypes
    if (params && params.mediaType) {
      mediaTypes = [params.mediaType]
    } else {
      mediaTypes = [AUDIO, IMAGE]
    }
    mediaTypes.forEach((mediaType) => {
      _state.results[mediaType].items = []
      _state.results[mediaType].count = 0
      _state.results[mediaType].page = undefined
      _state.results[mediaType].pageCount = 0
    })
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
