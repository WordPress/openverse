import { defineStore } from 'pinia'

import axios from 'axios'

import type { AudioDetail, ImageDetail, Media } from '~/models/media'
import type { SupportedMediaType } from '~/constants/media'
import type { FetchState } from '~/models/fetch-state'
import { initServices } from '~/stores/media/services'
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

    _updateFetchState(action: 'start' | 'end', option?: string) {
      action === 'start' ? this._startFetching() : this._endFetching(option)
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
        this.fetchMediaItem(type, id).then(() => {
          /** noop to prevent the promise return ignored warning */
        })
      } else {
        await this.fetchMediaItem(type, id)
      }
      /**
       * On the server, we await the related media to make sure it's rendered on the page.
       * On the client, we don't await it to render the whole page while the related media are loading.
       */
      if (process.server) {
        try {
          await useRelatedMediaStore().fetchMedia(type, id)
        } catch (error) {
          console.warn('Could not load related media: ', error)
        }
      } else {
        useRelatedMediaStore()
          .fetchMedia(type, id)
          .catch((error) =>
            console.warn('Could not load related media: ', error)
          )
      }
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
        const accessToken = this.$nuxt.$openverseApiToken
        const service = initServices[type](accessToken)
        this.mediaItem = this._addProviderName(await service.getMediaDetail(id))
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
