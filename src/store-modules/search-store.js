import findIndex from 'lodash.findindex'
import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import decodeMediaData from '~/utils/decode-media-data'
import {
  FETCH_AUDIO,
  FETCH_IMAGE,
  FETCH_MEDIA,
  HANDLE_MEDIA_ERROR,
  HANDLE_NO_MEDIA,
  SET_SEARCH_TYPE_FROM_URL,
  UPDATE_SEARCH_TYPE,
} from '~/constants/action-types'
import {
  FETCH_END_MEDIA,
  FETCH_MEDIA_ERROR,
  FETCH_START_MEDIA,
  MEDIA_NOT_FOUND,
  RESET_MEDIA,
  SET_AUDIO,
  SET_IMAGE,
  SET_IMAGE_PAGE,
  SET_MEDIA,
  SET_QUERY,
  SET_SEARCH_TYPE,
  UPDATE_FILTERS,
} from '~/constants/mutation-types'
import {
  SEND_RESULT_CLICKED_EVENT,
  SEND_SEARCH_QUERY_EVENT,
} from '~/constants/usage-data-analytics-types'
import { queryStringToSearchType } from '~/utils/search-query-transform'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { USAGE_DATA } from '~/constants/store-modules'

// const getSearchPath = () =>
//   window.location.pathname && window.location.pathname.includes('search')
//     ? window.location.pathname
//     : '/search'

/**
 * @type {{ audios: import('../store/types').AudioDetail[],
 * audiosCount: number, audioPage:number,
 * images: import('../store/types').ImageDetail[],
 * imagePage: number, imagesCount: number, query: {},
 * pageCount: {images: number, audios: number},
 * isFetching: {images: boolean, audios: boolean},
 * isFetchingError: {images: boolean, audios: boolean},
 * errorMessage: null, searchType: string, }}
 */
const state = {
  audios: [],
  audiosCount: 0,
  audioPage: 1,
  images: [],
  imagesCount: 0,
  imagePage: 1,
  pageCount: {
    images: 0,
    audios: 0,
  },
  isFetching: {
    audios: false,
    images: false,
  },
  isFetchingError: {
    audios: true,
    images: true,
  },
  errorMessage: null,
  searchType: ALL_MEDIA,
  query: {},
  audio: {},
  image: {},
}

const actions = (services) => ({
  async [FETCH_MEDIA]({ commit, dispatch, rootState }, params) {
    // does not send event if user is paginating for more results
    const { page, mediaType, q } = params
    if (!page) {
      dispatch(`${USAGE_DATA}/${SEND_SEARCH_QUERY_EVENT}`, {
        query: q,
        sessionId: rootState.user.usageSessionId,
      })
    }

    commit(FETCH_START_MEDIA, { mediaType })
    if (!params.page) {
      commit(RESET_MEDIA, { mediaType })
    }
    const queryParams = prepareSearchQueryParams(params)
    if (!Object.keys(services).includes(mediaType)) {
      throw new Error(`Cannot fetch unknown media type "${mediaType}"`)
    }
    await services[mediaType]
      .search(queryParams)
      .then(({ data }) => {
        commit(FETCH_END_MEDIA, { mediaType })
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
  async [FETCH_AUDIO]({ commit, dispatch, state, rootState }, params) {
    dispatch(`${USAGE_DATA}/${SEND_RESULT_CLICKED_EVENT}`, {
      query: state.query.q,
      resultUuid: params.id,
      resultRank: findIndex(state.audios, (img) => img.id === params.id),
      sessionId: rootState.user.usageSessionId,
    })
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
  async [FETCH_IMAGE]({ commit, dispatch, state, rootState }, params) {
    dispatch(`${USAGE_DATA}/${SEND_RESULT_CLICKED_EVENT}`, {
      query: state.query.q,
      resultUuid: params.id,
      resultRank: findIndex(state.images, (img) => img.id === params.id),
      sessionId: rootState.user.usageSessionId,
    })

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
  [HANDLE_NO_MEDIA]({ commit }, { mediaCount, mediaType }) {
    if (!mediaCount) {
      commit(FETCH_MEDIA_ERROR, {
        errorMessage: `No ${mediaType} found for this query`,
      })
    }
  },
  [SET_SEARCH_TYPE_FROM_URL]({ commit }, params) {
    commit(SET_SEARCH_TYPE, { searchType: queryStringToSearchType(params.url) })
    commit(UPDATE_FILTERS)
  },
  [UPDATE_SEARCH_TYPE]({ commit }, params) {
    commit(SET_SEARCH_TYPE, { searchType: params.searchType })
    commit(UPDATE_FILTERS)
  },
})

const mutations = {
  [FETCH_START_MEDIA](_state, { mediaType }) {
    const mediaPlural = `${mediaType}s`
    _state.isFetching[mediaPlural] = true
    _state.isFetchingError[mediaPlural] = false
  },
  [FETCH_END_MEDIA](_state, { mediaType }) {
    const mediaPlural = `${mediaType}s`
    _state.isFetching[mediaPlural] = false
  },
  [FETCH_MEDIA_ERROR](_state, params) {
    const { mediaType, errorMessage } = params
    const mediaPlural = `${mediaType}s`
    _state.isFetching[mediaPlural] = false
    _state.isFetchingError[mediaPlural] = true
    _state.errorMessage = errorMessage
  },
  [SET_AUDIO](_state, params) {
    _state.audio = decodeMediaData(params.audio, AUDIO)
  },
  [SET_IMAGE](_state, params) {
    _state.image = decodeMediaData(params.image)
  },
  [SET_IMAGE_PAGE](_state, params) {
    _state.imagePage = params.imagePage
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
    const mediaPlural = `${mediaType}s`
    let mediaToSet
    if (shouldPersistMedia) {
      mediaToSet = _state[`${mediaType}s`].concat(media)
    } else {
      mediaToSet = media
    }
    mediaToSet = mediaToSet.map((item) => decodeMediaData(item))
    _state[mediaPlural] = mediaToSet
    _state[`${mediaPlural}Count`] = mediaCount || 0
    _state[`${mediaType}Page`] = page || 1
    _state.pageCount[mediaPlural] = pageCount
  },
  [SET_QUERY](_state, params) {
    _state.query = Object.assign({}, _state.query, params.query)
    _state.images = []
  },
  [MEDIA_NOT_FOUND](_state, params) {
    throw new Error(`Media of type ${params.mediaType} not found`)
  },
  [SET_SEARCH_TYPE](_state, params) {
    _state.searchType = params.searchType
  },
  [RESET_MEDIA](_state, params) {
    const { mediaType } = params
    _state[`${mediaType}s`] = []
    _state[`${mediaType}sCount`] = 0
    _state[`${mediaType}Page`] = undefined
    _state.pageCount[`${mediaType}s`] = 0
  },
}

export default {
  state,
  actions,
  mutations,
}
