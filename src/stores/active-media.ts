import { defineStore } from 'pinia'

import type { SupportedMediaType } from '~/constants/media'
import type { Media } from '~/models/media'

export type MediaStatus = 'ejected' | 'playing' | 'paused' // 'ejected' means player is closed

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
export const useActiveMediaStore = defineStore(ACTIVE_MEDIA, {
  /* State */

  state: (): ActiveMediaState => ({
    type: null,
    id: null,
    status: 'ejected',
    message: null,
  }),

  actions: {
    /**
     * Sets a new media item as the active one.
     *
     * @param type - the type of the active media
     * @param id - the unique identifier of the active media
     * @param status - the current status of the active media
     */
    setActiveMediaItem({
      type,
      id,
      status = 'playing',
    }: {
      type: SupportedMediaType
      id: Media['id']
      status?: MediaStatus
    }) {
      this.type = type
      this.id = id
      this.status = status
    },

    pauseActiveMediaItem() {
      this.status = 'paused'
    },

    ejectActiveMediaItem() {
      this.status = 'ejected'
      this.id = null
      this.type = null
    },
    /**
     * Set the message associated with rendering/playback of the active media.
     *
     * @param message - the message to display to the user
     */
    setMessage({ message }: { message: string }) {
      this.message = message
    },
  },
})
