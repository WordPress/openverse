import {
  SET_ACTIVE_MEDIA_ITEM,
  UNSET_ACTIVE_MEDIA_ITEM,
} from './mutation-types'

/**
 * Stores information about the active media item.
 * @type {import('./types').ActiveMediaState}
 */
const state = {
  activeMediaType: null,
  activeMediaId: null,
}

const mutations = {
  /**
   * Set the active media item.
   * @param {import('./types').ActiveMediaState} _state
   * @param {'image' | 'audio' | null} type - the nature of the active media item
   * @param {string} id - the ID of the active media item
   */
  [SET_ACTIVE_MEDIA_ITEM](_state, { type, id }) {
    _state.activeMediaType = type
    _state.activeMediaId = id
  },
  /**
   * Clear the active media item.
   * @param {import('./types').ActiveMediaState} _state
   */
  [UNSET_ACTIVE_MEDIA_ITEM](_state) {
    _state.activeMediaType = null
    _state.activeMediaId = null
  },
}

export default {
  state,
  mutations,
}
