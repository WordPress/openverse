import { FETCH_IMAGE_PROVIDERS } from './action-types'

import {
  FETCH_IMAGE_PROVIDERS_END,
  SET_FETCH_IMAGES_ERROR,
  FETCH_IMAGE_PROVIDERS_START,
  SET_IMAGE_PROVIDERS,
  SET_PROVIDERS_FILTERS,
} from './mutation-types'

import previousImageProviders from '../data/existingImageProviders'

const state = {
  imageProviders: [],
  isFetchingImageProvidersError: false,
  isFetchingImageProviders: false,
}

const actions = (ImageProviderService) => ({
  [FETCH_IMAGE_PROVIDERS]({ commit }, params) {
    commit(SET_FETCH_IMAGES_ERROR, { isFetchingImageProvidersError: false })
    commit(FETCH_IMAGE_PROVIDERS_START)
    return ImageProviderService.getProviderStats(params)
      .then(({ data }) => {
        const sortedProviders = data.sort((sourceObjectA, sourceObjectB) => {
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
        commit(FETCH_IMAGE_PROVIDERS_END)
        commit(SET_IMAGE_PROVIDERS, { imageProviders: sortedProviders })
        commit(SET_PROVIDERS_FILTERS, { imageProviders: sortedProviders })
      })
      .catch((error) => {
        commit(SET_FETCH_IMAGES_ERROR, { isFetchingImageProvidersError: true })
        commit(SET_IMAGE_PROVIDERS, { imageProviders: previousImageProviders })
        throw new Error(error)
      })
  },
})

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [FETCH_IMAGE_PROVIDERS_START](_state) {
    _state.isFetchingImageProviders = true
  },
  [FETCH_IMAGE_PROVIDERS_END](_state) {
    _state.isFetchingImageProviders = false
  },
  [SET_FETCH_IMAGES_ERROR](_state, params) {
    _state.isFetchingImageProvidersError = params.isFetchingImageProvidersError
  },
  [SET_IMAGE_PROVIDERS](_state, params) {
    _state.imageProviders = params.imageProviders
  },
}

export default {
  state,
  actions,
  mutations,
}
