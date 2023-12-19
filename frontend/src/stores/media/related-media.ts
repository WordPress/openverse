import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import { parseFetchingError } from "~/utils/errors"
import { initServices } from "~/stores/media/services"

import type { FetchingError, FetchState } from "~/types/fetch-state"
import type { Media } from "~/types/media"
import type { SupportedMediaType } from "~/constants/media"

interface RelatedMediaState {
  mainMediaId: null | string
  media: Media[]
  fetchState: FetchState
}

export const useRelatedMediaStore = defineStore("related-media", {
  state: (): RelatedMediaState => ({
    mainMediaId: null,
    fetchState: { isFetching: false, hasStarted: false, fetchingError: null },
    media: [],
  }),

  getters: {
    getItemById:
      (state) =>
      (id: string): Media | undefined =>
        state.media.find((item) => item.id === id),
  },

  actions: {
    _endFetching(error?: FetchingError) {
      this.fetchState.fetchingError = error || null
      this.fetchState.hasStarted = true
      this.fetchState.isFetching = false
    },
    _startFetching() {
      this.fetchState.isFetching = true
      this.fetchState.hasStarted = true
      this.fetchState.fetchingError = null
    },
    _resetFetching() {
      this.fetchState.isFetching = false
      this.fetchState.hasStarted = false
      this.fetchState.fetchingError = null
    },

    async fetchMedia(mediaType: SupportedMediaType, id: string) {
      this._resetFetching()
      this.mainMediaId = id
      this._startFetching()
      this.media = []
      try {
        const accessToken = this.$nuxt.$openverseApiToken
        const service = initServices[mediaType](accessToken)
        this.media = (
          await service.getRelatedMedia<typeof mediaType>(id)
        ).results
        this._endFetching()

        return this.media.length
      } catch (error) {
        const errorData = parseFetchingError(error, mediaType, "related", {
          id,
        })

        this._endFetching(errorData)
        const { $sentry } = useNuxtApp()
        if ($sentry) {
          $sentry.captureException(error, { extra: { errorData } })
        } else {
          console.log("Sentry not available to capture exception", errorData)
        }
        return null
      }
    },
  },
})
