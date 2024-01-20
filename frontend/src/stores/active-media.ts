import { defineStore } from "pinia"

import type { SupportedMediaType } from "~/constants/media"
import type { AudioDetail, Media } from "~/types/media"

export type MediaStatus = "ejected" | "playing" | "paused" // 'ejected' means player is closed

export interface ActiveMediaState {
  type: SupportedMediaType | null
  id: Media["id"] | null
  status: MediaStatus
  /**
   * The i18n key for the message to display when rendering the active media.
   * Used to display playback errors.
   */
  message: string | null
  detail: AudioDetail | null
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
    detail: null,
  }),

  actions: {
    /**
     * Sets a new media item as the active one.
     *
     * @param type - the type of the active media
     * @param id - the unique identifier of the active media
     * @param detail - the object with audio detail properties
     * @param status - the current status of the active media
     */
    setActiveMediaItem({
      type,
      id,
      detail = undefined,
      status = "playing",
    }: {
      type: SupportedMediaType
      id: Media["id"]
      detail?: AudioDetail
      status?: MediaStatus
    }) {
      this.type = type
      this.id = id
      this.status = status
      if (detail) {
        this.detail = detail
      }
    },

    pauseActiveMediaItem() {
      this.status = "paused"
    },

    ejectActiveMediaItem() {
      this.status = "ejected"
      this.id = null
      this.type = null
      this.detail = null
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
