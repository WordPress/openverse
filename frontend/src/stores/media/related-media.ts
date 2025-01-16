import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import type { SupportedMediaType } from "#shared/constants/media"
import type { FetchingError, FetchState } from "#shared/types/fetch-state"
import type { Media } from "#shared/types/media"
import { useApiClient } from "~/composables/use-api-client"

interface RelatedMediaState {
  mainMediaId: null | string
  media: Media[]
  fetchState: FetchState
}

export const useRelatedMediaStore = defineStore("related-media", {
  state: (): RelatedMediaState => ({
    mainMediaId: null,
    fetchState: { status: "idle", error: null },
    media: [],
  }),

  getters: {
    getItemById:
      (state) =>
      (id: string): Media | undefined =>
        state.media.find((item) => item.id === id),
    isFetching: (state) => state.fetchState.status === "fetching",
  },

  actions: {
    _endFetching(error?: FetchingError) {
      if (error) {
        this.fetchState = { status: "error", error }
      } else {
        this.fetchState = { status: "success", error: null }
      }
    },
    _startFetching() {
      this.fetchState = { status: "fetching", error: null }
    },
    _resetFetching() {
      this.fetchState = { status: "idle", error: null }
    },

    async fetchMedia(mediaType: SupportedMediaType, id: string) {
      if (this.mainMediaId === id && this.media.length > 0) {
        return this.media
      }
      this._resetFetching()
      this.mainMediaId = id
      this._startFetching()
      this.media = []
      const client = useApiClient()

      try {
        this.media = await client.getRelatedMedia(mediaType, id)
        this._endFetching()

        return this.media
      } catch (error) {
        const { $processFetchingError } = useNuxtApp()
        const errorData = $processFetchingError(error, mediaType, "related", {
          id,
        })
        this._endFetching(errorData)
        return null
      }
    },
  },
})
