import {
  SET_ACTIVE_MEDIA_ITEM,
  UNSET_ACTIVE_MEDIA_ITEM,
} from '~/constants/mutation-types'

/**
 * Stores information about the active media item.
 * @return {import('./types').ActiveMediaState}
 */
const state = () => ({
  type: null,
  id: null,
})

const mutations = {
  /**
   * Set the active media item.
   * @param {import('./types').ActiveMediaState} _state
   * @param {object} payload
   * @param {'image' | 'audio' | null} payload.type - the nature of the active media item
   * @param {string} payload.id - the ID of the active media item
   */
  [SET_ACTIVE_MEDIA_ITEM](_state, { type, id }) {
    _state.type = type
    _state.id = id
  },
  /**
   * Clear the active media item.
   * @param {import('./types').ActiveMediaState} _state
   */
  [UNSET_ACTIVE_MEDIA_ITEM](_state) {
    _state.type = null
    _state.id = null
  },
}

export default {
  state,
  mutations,
}
