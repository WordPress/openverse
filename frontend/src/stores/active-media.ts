import { defineStore } from "pinia"

import type { SupportedMediaType } from "~/constants/media"
import type { MediaDetail } from "~/types/media"

export type MediaStatus = "ejected" | "playing" | "paused" // 'ejected' means player is closed

export interface ActiveMediaState {
  type: SupportedMediaType | null
  id: MediaDetail["id"] | null
  status: MediaStatus
  /**
   * The i18n key for the message to display when rendering the active media.
   * Used to display playback errors.
   */
  message: string | null
}

const ACTIVE_MEDIA = "active-media"

/**
 * Store information about the active media item.
 */
export const useActiveMediaStore = defineStore(ACTIVE_MEDIA, {
  /* State */

  state: (): ActiveMediaState => ({
    type: null,
    id: null,
    status: "ejected",
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
      status = "playing",
    }: {
      type: SupportedMediaType
      id: MediaDetail["id"]
      status?: MediaStatus
    }) {
      this.type = type
      this.id = id
      this.status = status
    },

    pauseActiveMediaItem() {
      this.status = "paused"
    },

    ejectActiveMediaItem() {
      this.status = "ejected"
      this.id = null
      this.type = null
    },
    /**
     * Set the message associated with rendering/playback of the active media.
     *
     * @param message - the i18n key of the message to display to the user
     */
    setMessage({ message }: { message: string | null }) {
      this.message = message
    },
  },
})
