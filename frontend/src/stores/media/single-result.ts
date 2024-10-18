import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import type {
  AudioDetail,
  DetailFromMediaType,
  ImageDetail,
} from "~/types/media"
import { isDetail, isMediaDetail } from "~/types/media"

import type { SupportedMediaType } from "~/constants/media"

import { useMediaStore } from "~/stores/media/index"
import { validateUUID } from "~/utils/query-utils"

import { FetchingError, FetchState } from "~/types/fetch-state"
import { useApiClient } from "~/composables/use-api-client"

export type MediaItemState = {
  mediaType: SupportedMediaType | null
  mediaId: string | null
  mediaItem: DetailFromMediaType<SupportedMediaType> | null
  fetchState: FetchState
}

export const useSingleResultStore = defineStore("single-result", {
  state: (): MediaItemState => ({
    mediaType: null,
    mediaId: null,
    mediaItem: null,
    fetchState: { isFetching: false, fetchingError: null },
  }),

  getters: {
    audio(state): AudioDetail | null {
      if (isDetail.audio(state.mediaItem)) {
        return state.mediaItem
      }
      return null
    },
    image(state): ImageDetail | null {
      if (isDetail.image(state.mediaItem)) {
        return state.mediaItem
      }
      return null
    },
  },

  actions: {
    _endFetching(error?: FetchingError) {
      this.fetchState.isFetching = false
      this.fetchState.fetchingError = error || null
    },
    _startFetching() {
      this.fetchState.isFetching = true
      this.fetchState.fetchingError = null
    },

    _updateFetchState(action: "start" | "end", option?: FetchingError) {
      if (action === "start") {
        this._startFetching()
      } else {
        this._endFetching(option)
      }
    },

    reset() {
      this.mediaItem = null
      this.mediaType = null
      this.mediaId = null
      this.fetchState.isFetching = false
      this.fetchState.fetchingError = null
    },

    /**
     * Set the media item with the display name of its provider
     * and its type. Reset the other media type item.
     * If the media item is null, reset both media items.
     */
    setMediaItem(mediaItem: AudioDetail | ImageDetail | null) {
      if (mediaItem) {
        this.mediaItem = mediaItem
        this.mediaType = mediaItem.frontendMediaType
        this.mediaId = mediaItem.id
      } else {
        this.mediaItem = null
        this.mediaType = null
        this.mediaId = null
      }
    },

    /**
     * If the item is already in the media store, reuse it.
     * Otherwise, set the media type and id, fetch the media
     * itself later.
     */
    setMediaById(type: SupportedMediaType, id: string) {
      if (this.mediaId === id && isMediaDetail(this.mediaItem, type)) {
        return
      }
      const existingItem = useMediaStore().getItemById(type, id)
      if (existingItem) {
        this.setMediaItem(existingItem)
      } else {
        this.mediaId = id
        this.mediaType = type
        this.mediaItem = null
      }
    },

    getExistingItem<T extends SupportedMediaType>(
      type: T,
      id: string
    ): DetailFromMediaType<T> | null {
      if (this.mediaId === id && isMediaDetail<T>(this.mediaItem, type)) {
        return this.mediaItem
      }
      const existingItem = useMediaStore().getItemById(type, id)
      if (existingItem) {
        return existingItem as DetailFromMediaType<T>
      }
      return null
    },

    /**
     * Check if the `id` matches the `mediaId` and the media item
     * is already fetched. If middleware only set the `id` and
     * did not set the media, fetch the media item.
     */
    async fetch<T extends SupportedMediaType>(type: T, id: string | null) {
      if (!id || !validateUUID(id)) {
        this._endFetching({
          code: "ERR_UNKNOWN",
          requestKind: "single-result",
          searchType: type,
        } as FetchingError)
        return null
      }
      const existingItem = this.getExistingItem(type, id)
      if (existingItem) {
        return existingItem
      }

      this._updateFetchState("start")

      // When fetch is called by the middleware, the app context is not available during the error handling,
      // so we need to use the `useNuxtApp` here, outside the catch clause, to access the app context.
      const { $processFetchingError } = useNuxtApp()

      const client = useApiClient()

      try {
        const item = await client.getSingleMedia(type, id)

        this.setMediaItem(item)
        this._updateFetchState("end")

        return item as DetailFromMediaType<typeof type>
      } catch (error) {
        const errorData = $processFetchingError(error, type, "single-result", {
          id,
        })
        this._updateFetchState("end", errorData)
        return null
      }
    },
  },
})
