import {
  FETCH_MEDIA_TYPE_PROVIDERS,
  FETCH_MEDIA_PROVIDERS,
} from './action-types'

import {
  SET_PROVIDER_FETCH_ERROR,
  FETCH_MEDIA_PROVIDERS_END,
  FETCH_MEDIA_PROVIDERS_START,
  SET_MEDIA_PROVIDERS,
  SET_PROVIDERS_FILTERS,
} from './mutation-types'

import previousImageProviders from '../data/existingImageProviders'
import previousAudioProviders from '../data/existingAudioProviders'

const AUDIO = 'audio'
const IMAGE = 'image'

const existingProviders = {
  [AUDIO]: previousAudioProviders,
  [IMAGE]: previousImageProviders,
}

const sortProviders = (data) => {
  return data.sort((sourceObjectA, sourceObjectB) => {
    const nameA = sourceObjectA.source_name.toUpperCase()
    const nameB = sourceObjectB.source_name.toUpperCase()

    if (nameA < nameB) {
      return -1
    }

    if (nameA > nameB) {
      return 1
    }

    return 0
  })
}

const state = {
  audioProviders: [],
  imageProviders: [],
  isFetchingAudioProvidersError: false,
  isFetchingImageProvidersError: false,
  isFetchingAudioProviders: false,
  isFetchingImageProviders: false,
}

const actions = (AudioProviderService, ImageProviderService) => ({
  [FETCH_MEDIA_PROVIDERS]({ dispatch }, params) {
    return Promise.all([
      dispatch(FETCH_MEDIA_TYPE_PROVIDERS, { ...params, mediaType: AUDIO }),
      dispatch(FETCH_MEDIA_TYPE_PROVIDERS, { ...params, mediaType: IMAGE }),
    ])
  },
  [FETCH_MEDIA_TYPE_PROVIDERS]({ commit }, params) {
    console.log('fetching media providers, params: ', params)
    const { mediaType } = params
    commit(SET_PROVIDER_FETCH_ERROR, { mediaType, error: false })
    commit(FETCH_MEDIA_PROVIDERS_START, { mediaType })
    const providerService =
      mediaType === AUDIO ? AudioProviderService : ImageProviderService
    let sortedProviders
    return providerService
      .getProviderStats()
      .then(({ data }) => {
        sortedProviders = sortProviders(data)
      })
      .catch((error) => {
        console.error(
          `Error getting ${mediaType} providers: ${error}.  Will use saved provider data instead `
        )
        sortedProviders = existingProviders[mediaType]
        commit(SET_PROVIDER_FETCH_ERROR, { mediaType, error: true })
      })
      .finally(() => {
        commit(FETCH_MEDIA_PROVIDERS_END, { mediaType })
        commit(SET_MEDIA_PROVIDERS, {
          mediaType,
          providers: sortedProviders,
        })
        commit(SET_PROVIDERS_FILTERS, {
          mediaType,
          providers: sortedProviders,
        })
      })
  },
})

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [FETCH_MEDIA_PROVIDERS_START](_state, { mediaType }) {
    if (mediaType === AUDIO) {
      _state.isFetchingAudioProviders = true
    } else {
      _state.isFetchingImageProviders = true
    }
  },
  [FETCH_MEDIA_PROVIDERS_END](_state, { mediaType }) {
    if (mediaType === AUDIO) {
      _state.isFetchingAudioProviders = false
    } else {
      _state.isFetchingImageProviders = false
    }
  },
  [SET_PROVIDER_FETCH_ERROR](_state, params) {
    params.mediaType === AUDIO
      ? (_state.isFetchingAudioProvidersError = params.error)
      : (_state.isFetchingImageProvidersError = params.error)
  },
  [SET_MEDIA_PROVIDERS](_state, params) {
    params.mediaType === AUDIO
      ? (_state.audioProviders = params.providers)
      : (_state.imageProviders = params.providers)
  },
}

export default {
  state,
  actions,
  mutations,
}
