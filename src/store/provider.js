import MediaProviderService from '~/data/media-provider-service'
import { AUDIO, IMAGE } from '~/constants/media'
import {
  FETCH_MEDIA_TYPE_PROVIDERS,
  FETCH_MEDIA_PROVIDERS,
} from '~/constants/action-types'

import {
  SET_PROVIDER_FETCH_ERROR,
  FETCH_MEDIA_PROVIDERS_END,
  FETCH_MEDIA_PROVIDERS_START,
  SET_MEDIA_PROVIDERS,
  SET_PROVIDERS_FILTERS,
} from '~/constants/mutation-types'
import { capital } from 'case'
import { SEARCH } from '~/constants/store-modules'
import { warn } from '~/utils/console'

const AudioProviderService = MediaProviderService(AUDIO)
const ImageProviderService = MediaProviderService(IMAGE)

const sortProviders = (data) => {
  return data.sort((sourceObjectA, sourceObjectB) => {
    const nameA = sourceObjectA.source_name.toUpperCase()
    const nameB = sourceObjectB.source_name.toUpperCase()
    return nameA.localeCompare(nameB)
  })
}

export const state = () => ({
  audioProviders: [],
  imageProviders: [],
  isFetchingAudioProvidersError: false,
  isFetchingImageProvidersError: false,
  isFetchingAudioProviders: false,
  isFetchingImageProviders: false,
})

export const getters = {
  getProviderName: (state, getters, rootState) => (providerCode) => {
    const mediaType = rootState.search.mediaType
    const providersList = state[`${mediaType}Providers`]
    if (!providersList) {
      return capital(providerCode) || ''
    }

    const provider = providersList.filter(
      (p) => p.source_name === providerCode
    )[0]

    return provider ? provider.display_name : capital(providerCode) || ''
  },
}

export const createActions = (services) => ({
  async [FETCH_MEDIA_PROVIDERS]({ dispatch }, params) {
    return Promise.all([
      dispatch(FETCH_MEDIA_TYPE_PROVIDERS, { ...params, mediaType: AUDIO }),
      dispatch(FETCH_MEDIA_TYPE_PROVIDERS, { ...params, mediaType: IMAGE }),
    ])
  },
  [FETCH_MEDIA_TYPE_PROVIDERS]({ commit }, params) {
    const { mediaType } = params
    commit(SET_PROVIDER_FETCH_ERROR, { mediaType, error: false })
    commit(FETCH_MEDIA_PROVIDERS_START, { mediaType })
    const providerService = services[mediaType]
    let sortedProviders
    return providerService
      .getProviderStats()
      .then(({ data }) => {
        sortedProviders = sortProviders(data)
      })
      .catch((error) => {
        warn(
          `Error getting ${mediaType} providers: ${error}. Will use saved provider data instead.`
        )
        commit(SET_PROVIDER_FETCH_ERROR, { mediaType, error: true })
      })
      .finally(() => {
        commit(FETCH_MEDIA_PROVIDERS_END, { mediaType })
        commit(SET_MEDIA_PROVIDERS, {
          mediaType,
          providers: sortedProviders,
        })
        commit(
          `${SEARCH}/${SET_PROVIDERS_FILTERS}`,
          {
            mediaType,
            providers: sortedProviders,
          },
          { root: true }
        )
      })
  },
})

export const actions = createActions({
  [IMAGE]: ImageProviderService,
  [AUDIO]: AudioProviderService,
})

export const mutations = {
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
  getters,
  state,
  mutations,
  actions,
}
