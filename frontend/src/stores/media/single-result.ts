import { defineStore } from "pinia"

import axios from "axios"

import type { FetchState } from "~/types/fetch-state"
import type {
  AudioDetail,
  DetailFromMediaType,
  ImageDetail,
} from "~/types/media"
import { isDetail } from "~/types/media"

import type { SupportedMediaType } from "~/constants/media"
import { AUDIO, IMAGE } from "~/constants/media"
import { markFakeSensitive } from "~/utils/content-safety"

import { initServices } from "~/stores/media/services"
import { useMediaStore } from "~/stores/media/index"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useProviderStore } from "~/stores/provider"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { warn } from "~/utils/console"

export type MediaItemState = {
  [k in SupportedMediaType]: DetailFromMediaType<k> | null
} & {
  mediaType: SupportedMediaType | null
  mediaId: string | null
  fetchState: FetchState
}

export const useSingleResultStore = defineStore("single-result", {
  state: (): MediaItemState => ({
    mediaType: null,
    mediaId: null,
    image: null,
    audio: null,
    fetchState: { isFetching: false, hasStarted: false, fetchingError: null },
  }),

  actions: {
    _endFetching(error?: string) {
      this.fetchState.isFetching = false
      this.fetchState.fetchingError = error || null
    },
    _startFetching() {
      this.fetchState.isFetching = true
      this.fetchState.hasStarted = true
      this.fetchState.fetchingError = null
    },

    _updateFetchState(action: "start" | "end", option?: string) {
      action === "start" ? this._startFetching() : this._endFetching(option)
    },

    _addProviderName<T extends ImageDetail | AudioDetail>(mediaItem: T): T {
      const providerStore = useProviderStore()

      mediaItem.providerName = providerStore.getProviderName(
        mediaItem.provider,
        mediaItem.frontendMediaType
      )
      if (mediaItem.source) {
        mediaItem.sourceName = providerStore.getProviderName(
          mediaItem.source,
          mediaItem.frontendMediaType
        )
      }
      return mediaItem
    },
    reset() {
      this.audio = null
      this.image = null
      this.mediaType = null
      this.mediaId = null
      this.fetchState.isFetching = false
      this.fetchState.hasStarted = false
      this.fetchState.fetchingError = null
    },

    /**
     * Set the media item with the display name of its provider
     * and its type. Reset the other media type item.
     * If the media item is null, reset both media items.
     */
    setMediaItem(mediaItem: AudioDetail | ImageDetail | null) {
      if (isDetail.audio(mediaItem)) {
        this.audio = this._addProviderName(mediaItem)
        this.mediaType = AUDIO
        this.image = null
      } else if (isDetail.image(mediaItem)) {
        this.image = this._addProviderName(mediaItem)
        this.mediaType = IMAGE
        this.audio = null
      } else {
        this.image = null
        this.audio = null
        this.mediaType = null
      }
    },

    /**
     * If the item is already in the media store, reuse it.
     * Otherwise, set the media type and id, fetch the media
     * itself later.
     */
    setMediaById(type: SupportedMediaType, id: string) {
      this.reset()
      const existingItem = useMediaStore().getItemById(type, id)
      if (existingItem) {
        this.setMediaItem(existingItem)
      } else {
        this.mediaId = id
        this.mediaType = type
      }
    },

    /**
     * On the server, make sure that the related media is rendered
     * by awaiting the response.
     * On the client, render the page while loading the related media by
     * not awaiting the related media response.
     */
    async fetchRelatedMedia(type: SupportedMediaType, id: string) {
      if (process.server) {
        try {
          await useRelatedMediaStore().fetchMedia(type, id)
        } catch (error) {
          warn("Could not load related media: ", error)
        }
      } else {
        useRelatedMediaStore()
          .fetchMedia(type, id)
          .catch((error) => {
            warn("Could not load related media: ", error)
            this.$nuxt.$sentry.captureException(error)
          })
      }
    },

    /**
     * Check if the `id` matches the `mediaId` and the media item
     * is already fetched. If middleware only set the `id` and
     * did not set the media, fetch the media item.
     *
     * Fetch the related media if necessary.
     */
    async fetch(
      type: SupportedMediaType,
      id: string,
      options?: { fetchRelated: boolean }
    ) {
      const itemFetched = this.mediaId === id && !!this[type]
      if (!itemFetched) {
        try {
          await this.fetchMediaItem(type, id)
        } catch (error) {
          await this.handleFetchError(error)
        }
      }

      const shouldFetchRelated = options?.fetchRelated ?? true
      if (shouldFetchRelated) {
        await this.fetchRelatedMedia(type, id)
      }
    },

    async handleFetchError(error: unknown) {
      this.reset()
      this._updateFetchState("end", JSON.stringify(error))

      /**
       * Only send the error to Sentry if it is not a 404.
       */
      if (!(axios.isAxiosError(error) && error.response?.status === 404)) {
        this.$nuxt.$sentry.captureException(error)
      }
      /**
       * Show the error page. Use the response code if it is an axios error; 404 otherwise.
       */
      const statusCode = axios.isAxiosError(error)
        ? error.response?.status ?? 404
        : 404
      this.$nuxt.error({ statusCode, message: JSON.stringify(error) })
    },
    /**
     * Fetch the media item from the API.
     */
    async fetchMediaItem(type: SupportedMediaType, id: string) {
      this._updateFetchState("start")
      const accessToken = this.$nuxt.$openverseApiToken
      const service = initServices[type](accessToken)
      const item = this._addProviderName(await service.getMediaDetail(id))

      // Fake ~50% of results as mature. This leaves actual mature results unchanged.
      const featureFlagStore = useFeatureFlagStore()
      if (featureFlagStore.isOn("fake_sensitive")) {
        markFakeSensitive(item)
      }

      this.setMediaItem(item)

      this._updateFetchState("end")
    },
  },
})
