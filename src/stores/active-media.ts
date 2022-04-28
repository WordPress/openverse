import { defineStore } from 'pinia'
import { reactive, readonly, toRefs } from '@nuxtjs/composition-api'

import type { SupportedMediaType } from '~/constants/media'
import type { Media } from '~/models/media'

type MediaStatus = 'ejected' | 'playing' | 'paused' // 'ejected' means player is closed

export interface ActiveMediaState {
  type: SupportedMediaType | null
  id: Media['id'] | null
  status: MediaStatus
  message: string | null
}

const ACTIVE_MEDIA = 'active-media'

/**
 * Store information about the active media item.
 */
export const useActiveMediaStore = defineStore(ACTIVE_MEDIA, () => {
  /* State */

  const state: ActiveMediaState = reactive({
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

  /* Actions */

  /**
   * Sets a new media item as the active one.
   *
   * @param type - the type of the active media
   * @param id - the unique identifier of the active media
   * @param status - the current status of the active media
   */
  function setActiveMediaItem({
    type,
    id,
    status = 'playing',
  }: {
    type: SupportedMediaType
    id: Media['id']
    status?: MediaStatus
  }) {
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
   * Set the message associated with rendering/playback of the active media.
   *
   * @param message - the message to display to the user
   */
  function setMessage({ message }: { message: string }) {
    state.message = message
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
