import { SET_EMBEDDED, SET_REFERRED } from '~/store-modules/mutation-types'

const state = {
  isEmbedded: true,
  isReferredFromCc: false,
}

const mutations = {
  [SET_EMBEDDED](_state, params) {
    _state.isEmbedded = params.isEmbedded
  },
  [SET_REFERRED](_state, params) {
    _state.isReferredFromCc = params.isReferredFromCc
  },
}

export default {
  state,
  mutations,
}
