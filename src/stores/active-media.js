import { defineStore } from 'pinia'
import { reactive, readonly, toRefs } from '@nuxtjs/composition-api'

const ACTIVE_MEDIA = 'active-media'

/**
 * Store information about the active media item.
 */
export const useActiveMediaStore = defineStore(ACTIVE_MEDIA, () => {
  /**
   * `reactive` returns UnwrapRef<T> type, but the Vue docs recommend using the
   * type of <T> for typing it instead:
   * https://vuejs.org/guide/typescript/composition-api.html#typing-reactive
   * @type {import('../store/types').ActiveMediaState}
   */
  const state = reactive({
    type: null,
    id: null,
    status: 'ejected',
    message: null,
  })
  /**
   * Only the properties used by components are exported as refs.
   * `status` is not used anywhere in the components.
   */
  const { type, id, message } = toRefs(state)

  // Actions
  /**
   * @param {object} payload
   * @param {'audio'} payload.type
   * @param {string} payload.id
   * @param {'ejected' | 'playing' | 'paused'} payload.status
   */
  function setActiveMediaItem({ type, id, status = 'playing' }) {
    state.type = type
    state.id = id
    state.status = status
  }
  function pauseActiveMediaItem() {
    state.status = 'paused'
  }
  function ejectActiveMediaItem() {
    state.status = 'ejected'
    state.id = null
    state.type = null
  }

  /**
   * @param {object} params
   * @param {string} params.message
   */
  function setMessage(params) {
    state.message = params.message
  }

  return {
    type: readonly(type),
    id: readonly(id),
    message: readonly(message),
    state: readonly(state),

    setActiveMediaItem,
    pauseActiveMediaItem,
    ejectActiveMediaItem,
    setMessage,
  }
})
