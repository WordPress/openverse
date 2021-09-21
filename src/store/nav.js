import { SET_EMBEDDED, SET_REFERRED } from '~/constants/mutation-types'

export const state = () => ({
  isEmbedded: true,
})

export const mutations = {
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
