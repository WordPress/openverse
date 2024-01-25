import { decodeMediaData, useRequestEvent } from "#imports"

import { defineStore } from "pinia"

import axios from "axios"

import { parseFetchingError } from "~/utils/errors"
import { mediaSlug, DEFAULT_REQUEST_TIMEOUT } from "~/utils/query-utils"

import { FetchingError, FetchState } from "~/types/fetch-state"
import type { AudioDetail, ImageDetail, Media } from "~/types/media"
import type { SupportedMediaType } from "~/constants/media"
import type { PaginatedApiMediaResult } from "~/types/api"

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

    async fetchMedia(
      mediaType: SupportedMediaType,
      id: string,
      baseUrl?: string
    ) {
      if (this.mainMediaId === id && this.media.length > 0) {
        return this.media
      }
      this._resetFetching()
      this.mainMediaId = id
      this._startFetching()
      this.media = []
      const url = `/api/${mediaSlug(mediaType)}/${id}/related/`
      const params = mediaType === "audio" ? { peaks: true } : {}

      let baseURL = baseUrl ? baseUrl : null
      if (!baseURL) {
        const nitroOrigin = useRequestEvent()?.context?.siteConfigNitroOrigin
        baseURL = nitroOrigin ? nitroOrigin : location?.origin
        baseURL = baseURL.replace("localhost", "0.0.0.0")
      }
      try {
        const res = await axios.get<PaginatedApiMediaResult>(url, {
          timeout: DEFAULT_REQUEST_TIMEOUT,
          params,
          baseURL,
        })
        this.media = (res.data.results ?? []).map(
          (item: AudioDetail | ImageDetail) => decodeMediaData(item, mediaType)
        )
        this._endFetching()

        return this.media
      } catch (error) {
        const errorData = parseFetchingError(error, mediaType, "related", {
          id,
        })

        this._endFetching(errorData)

        console.warn(error, { extra: errorData })
        return null
      }
    },
  },
})
