import { defineStore } from "pinia"

import { useNuxtApp } from "#app"

import type { SupportedMediaType } from "~/constants/media"
import type { Media } from "~/types/media"
import { audioErrorMessages } from "~/constants/audio"
import { warn } from "~/utils/console"

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
      id: Media["id"]
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
    playAudio(audio: HTMLAudioElement | undefined) {
      const playPromise = audio?.play()
      // Check if the audio can be played successfully
      if (playPromise === undefined) {
        warn("Play promise is undefined")
        return
      }
      playPromise.catch((err) => {
        const message = Object.keys(audioErrorMessages).includes(err.name)
          ? audioErrorMessages[err.name as keyof typeof audioErrorMessages]
          : "err_unknown"
        if (message === "err_unknown") {
          const { $sentry } = useNuxtApp()
          $sentry.captureException(err)
        }
        this.setMessage({ message })
        audio?.pause()
      })
    },
  },
})
