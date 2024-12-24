import { useNuxtApp, useRequestEvent } from "#imports"

import { defineStore } from "pinia"
import { getProxyRequestHeaders } from "h3"

import type { SupportedMediaType } from "#shared/constants/media"
import type { FetchingError, FetchState } from "#shared/types/fetch-state"
import type { Media } from "#shared/types/media"
import type { MediaResult } from "~/data/api-service"
import { decodeMediaData } from "~/utils/decode-media-data"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useApiClient } from "~/composables/use-api-client"

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
      if (this.mainMediaId === id && this.media.length > 0) {
        return this.media
      }
      this._resetFetching()
      this.mainMediaId = id
      this._startFetching()
      this.media = []

      const ffStore = useFeatureFlagStore()
      const proxyEnabled = ffStore.isOn("proxy_requests")

      let media: Media[] = []

      if (proxyEnabled) {
        const event = useRequestEvent()
        const headers = event ? getProxyRequestHeaders(event) : {}
        const res = await $fetch<MediaResult<Media[]>>(
          `/api/related/${mediaType}/${id}`,
          headers
        )
        if (res) {
          media = res.results.map((media: Media) =>
            decodeMediaData(media, mediaType)
          )
        } else {
          this._endFetching({ message: "error" } as FetchingError)
          return null
        }
      } else {
        const client = useApiClient()

        try {
          media = await client.getRelatedMedia(mediaType, id)
        } catch (error) {
          const { $processFetchingError } = useNuxtApp()
          const errorData = $processFetchingError(error, mediaType, "related", {
            id,
          })
          this._endFetching(errorData)
          return null
        }
      }
      this.media = media
    },
  },
})
