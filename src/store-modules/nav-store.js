import { SET_EMBEDDED } from '~/store-modules/mutation-types'

const state = {
  isEmbedded: true,
}

const mutations = {
  [SET_EMBEDDED](_state, params) {
    _state.isEmbedded = params.isEmbedded
  },
}

export default {
  state,
  mutations,
}
