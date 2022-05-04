import { defineStore } from 'pinia'

import axios from 'axios'

import type { AudioDetail, ImageDetail, Media } from '~/models/media'
import type { SupportedMediaType } from '~/constants/media'
import {
  FetchState,
  initialFetchState,
  updateFetchState,
} from '~/composables/use-fetch-state'
import { services } from '~/stores/media/services'
import { useMediaStore } from '~/stores/media/index'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import { useProviderStore } from '~/stores/provider'

export type MediaItemState =
  | {
      mediaType: 'audio'
      mediaItem: AudioDetail
      fetchState: FetchState
    }
  | {
      mediaType: 'image'
      mediaItem: ImageDetail
      fetchState: FetchState
    }
  | {
      mediaType: null
      mediaItem: null
      fetchState: FetchState
    }

export const useSingleResultStore = defineStore('single-result', {
  state: (): MediaItemState => ({
    mediaItem: null,
    mediaType: null,
    fetchState: initialFetchState,
  }),

  actions: {
    _updateFetchState(action: 'end' | 'start', option?: string) {
      this.fetchState = updateFetchState(this.fetchState, action, option)
    },

    _addProviderName(mediaItem: Media) {
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

    /**
     * If the result is available in the media store (from search results or related media),
     * we can re-use it. Otherwise, we fetch it from the API.
     * The media objects from the search results currently don't have filetype or filesize properties.
     *
     * @param type - media type of the item to fetch.
     * @param id - string id of the item to fetch.
     */
    async fetch(type: SupportedMediaType, id: string) {
      const mediaStore = useMediaStore()
      const existingItem = mediaStore.getItemById(type, id)

      if (existingItem) {
        this.mediaType = existingItem.frontendMediaType
        this.mediaItem = this._addProviderName(existingItem)
      } else {
        await this.fetchMediaItem(type, id)
      }
      await useRelatedMediaStore().fetchMedia(type, id)
    },
    /**
     * Fetches a media item from the API.
     *
     * @param type - media type of the item to fetch.
     * @param id - string id of the item to fetch.
     */
    async fetchMediaItem(type: SupportedMediaType, id: string) {
      try {
        this._updateFetchState('start')
        this.mediaItem = this._addProviderName(
          await services[type].getMediaDetail(id)
        )
        this.mediaType = type

        this._updateFetchState('end')
      } catch (error: unknown) {
        this.mediaItem = null
        this.mediaType = type
        if (axios.isAxiosError(error) && error.response?.status === 404) {
          throw new Error(`Media of type ${type} with id ${id} not found`)
        } else {
          this.handleMediaError(error)
        }
      }
    },

    /**
     * Throws a new error with a new error message.
     */
    handleMediaError(error: unknown) {
      let errorMessage
      if (axios.isAxiosError(error)) {
        errorMessage =
          error.response?.status === 500
            ? 'There was a problem with our servers'
            : `Request failed with status ${
                error.response?.status ?? 'unknown'
              }`
      } else {
        errorMessage =
          error instanceof Error ? error.message : 'Oops! Something went wrong'
      }

      this._updateFetchState('end', errorMessage)
      throw new Error(errorMessage)
    },
  },
})
