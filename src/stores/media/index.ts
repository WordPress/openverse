import { defineStore } from 'pinia'

import axios from 'axios'

import { hash, rand as prng } from '~/utils/prng'
import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import type { DetailFromMediaType, Media } from '~/models/media'
import {
  FetchState,
  initialFetchState,
  updateFetchState,
} from '~/composables/use-fetch-state'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedMediaTypes,
} from '~/constants/media'
import { services } from '~/stores/media/services'
import { isSearchTypeSupported, useSearchStore } from '~/stores/search'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import { deepFreeze } from '~/utils/deep-freeze'

export type MediaStoreResult = {
  count: number
  pageCount: number
  page: number | undefined
  items: Record<string, Media>
}

export interface MediaState {
  results: {
    audio: MediaStoreResult
    image: MediaStoreResult
  }
  mediaFetchState: {
    audio: FetchState
    image: FetchState
  }
}

export const initialResults = deepFreeze({
  count: 0,
  page: undefined,
  pageCount: 0,
  items: {},
}) as MediaStoreResult

export const useMediaStore = defineStore('media', {
  state: (): MediaState => ({
    results: {
      [AUDIO]: { ...initialResults },
      [IMAGE]: { ...initialResults },
    },
    mediaFetchState: {
      [AUDIO]: { ...initialFetchState },
      [IMAGE]: { ...initialFetchState },
    },
  }),

  getters: {
    _searchType() {
      const searchStore = useSearchStore()
      return searchStore.searchType
    },
    getItemById: (state) => {
      return (mediaType: SupportedMediaType, id: string): Media | undefined => {
        const itemFromSearchResults = state.results[mediaType].items[id]
        if (itemFromSearchResults) return itemFromSearchResults
        return useRelatedMediaStore().getItemById(id)
      }
    },

    /**
     * Returns object with a key for each supported media type and arrays of media items for each.
     */
    resultItems(state) {
      return supportedMediaTypes.reduce(
        (items, type) => ({
          ...items,
          [type]: Object.values(state.results[type].items),
        }),
        {} as Record<SupportedMediaType, Media[]>
      )
    },

    /**
     * Returns result item counts for each supported media type.
     */
    resultCountsPerMediaType(): [SupportedMediaType, number][] {
      return supportedMediaTypes.map((type) => [type, this.results[type].count])
    },

    /**
     * Returns the total count of results for selected search type, sums all media results for ALL_MEDIA or additional types.
     * If the count is more than 10000, returns 10000 to match the API result.
     */
    resultCount(state) {
      const types = (
        this._searchType === ALL_MEDIA ||
        !isSearchTypeSupported(this._searchType)
          ? supportedMediaTypes
          : [this._searchType]
      ) as SupportedMediaType[]
      const count = types.reduce(
        (sum, mediaType) => sum + state.results[mediaType].count,
        0
      )
      return Math.min(count, 10000)
    },

    /**
     * Search fetching state for selected search type. For 'All content', aggregates
     * the values for supported media types.
     */
    fetchState(): FetchState {
      if (this._searchType === ALL_MEDIA) {
        /**
         * For all_media, we return the error for the first media type that has an error.
         */
        const findFirstError = () => {
          for (const type of supportedMediaTypes) {
            if (this.mediaFetchState[type].fetchingError) {
              return this.mediaFetchState[type].fetchingError
            }
          }
          return null
        }
        const atLeastOne = (property: keyof FetchState) =>
          supportedMediaTypes.some(
            (type) => this.mediaFetchState[type][property]
          )

        return {
          isFetching: atLeastOne('isFetching'),
          fetchingError: findFirstError(),
          canFetch: atLeastOne('canFetch'),
          hasStarted: atLeastOne('hasStarted'),
          isFinished: supportedMediaTypes.every(
            (type) => this.mediaFetchState[type].isFinished
          ),
        }
      } else if (isSearchTypeSupported(this._searchType)) {
        return this.mediaFetchState[this._searchType]
      } else {
        return initialFetchState
      }
    },

    allMedia(): Media[] {
      const media = this.resultItems

      // Seed the random number generator with the ID of
      // the first search result, so the non-image
      // distribution is the same on repeated searches
      const seedString = media[IMAGE][0]?.id
      let seed: number
      if (typeof seedString === 'string') {
        seed = hash(seedString)
      } else {
        let otherTypeId = 'string'
        for (const type of supportedMediaTypes.slice(1)) {
          if (typeof media[type][0]?.id === 'string') {
            otherTypeId = media[type][0].id
            break
          }
        }
        seed = hash(otherTypeId)
      }
      const rand = prng(seed)
      const randomIntegerInRange = (min: number, max: number) =>
        Math.floor(rand() * (max - min + 1)) + min
      /**
       * When navigating from All page to Audio page, VAllResultsGrid is displayed
       * for a short period of time. Then media['image'] is undefined, and it throws an error
       * `TypeError: can't convert undefined to object`. To fix it, we add `|| {}` to the media['image'].
       */
      /**
       * First, set the results to all images
       */
      const newResults = media.image

      // push other items into the list, using a random index.
      let nonImageIndex = 1
      for (const type of supportedMediaTypes.slice(1)) {
        for (const item of media[type]) {
          newResults.splice(nonImageIndex, 0, item)
          // TODO: Fix the algorithm. Currently, when there is no images, the nonImageIndex can get higher
          //  than general index, and items can get discarded.
          if (nonImageIndex > newResults.length + 1) break
          nonImageIndex = randomIntegerInRange(
            nonImageIndex + 1,
            nonImageIndex + 6
          )
        }
      }

      return newResults
    },
  },

  actions: {
    _updateFetchState(
      mediaType: SupportedMediaType,
      action: 'reset' | 'start' | 'end' | 'finish',
      option?: string
    ) {
      this.mediaFetchState[mediaType] = updateFetchState(
        this.mediaFetchState[mediaType],
        action,
        option
      )
    },

    setMedia<T extends SupportedMediaType>(params: {
      mediaType: T
      media: Record<string, DetailFromMediaType<T>>
      mediaCount: number
      page: number | undefined
      pageCount: number
      shouldPersistMedia: boolean | undefined
    }) {
      const {
        mediaType,
        media,
        mediaCount,
        page,
        pageCount,
        shouldPersistMedia,
      } = params
      let mediaToSet
      if (shouldPersistMedia) {
        mediaToSet = { ...this.results[mediaType].items, ...media } as Record<
          string,
          DetailFromMediaType<T>
        >
      } else {
        mediaToSet = media
      }
      const mediaPage = page || 1
      this.results[mediaType].items = mediaToSet
      this.results[mediaType].count = mediaCount || 0
      this.results[mediaType].page = mediaCount === 0 ? undefined : mediaPage
      this.results[mediaType].pageCount = pageCount
      if (mediaPage >= pageCount) {
        this._updateFetchState(mediaType, 'finish')
      }
    },

    mediaNotFound(mediaType: SupportedMediaType) {
      throw new Error(`Media of type ${mediaType} not found`)
    },

    /**
     * Clears the items for all passed media types, and resets fetch state.
     */
    resetMedia(mediaType: SupportedMediaType) {
      this.results[mediaType].items = {}
      this.results[mediaType].count = 0
      this.results[mediaType].page = undefined
      this.results[mediaType].pageCount = 0
    },

    resetFetchState() {
      for (const mediaType of supportedMediaTypes) {
        this._updateFetchState(mediaType, 'reset')
      }
    },

    /**
     * Calls `fetchSingleMediaType` for selected media type(s). Can be called by changing the search query
     * (search term or filter item), or by clicking 'Load more' button.
     * If the search query changed, fetch state is reset, otherwise only the media types for which
     * fetchState.isFinished is not true are fetched.
     */
    async fetchMedia(payload: { shouldPersistMedia?: boolean } = {}) {
      const mediaType = this._searchType
      if (!payload.shouldPersistMedia) {
        this.resetFetchState()
      }
      const mediaToFetch = (
        (mediaType !== ALL_MEDIA
          ? [mediaType]
          : [IMAGE, AUDIO]) as SupportedMediaType[]
      ).filter((type) => this.mediaFetchState[type].canFetch)
      await Promise.all(
        mediaToFetch.map((type) =>
          this.fetchSingleMediaType({
            mediaType: type,
            shouldPersistMedia: Boolean(payload.shouldPersistMedia),
          })
        )
      )
    },

    clearMedia() {
      supportedMediaTypes.forEach((mediaType) => {
        this.resetMedia(mediaType)
      })
    },

    /**
     * @param mediaType - the mediaType to fetch (do not use 'All_media' here)
     * @param shouldPersistMedia - whether the existing media should be added to or replaced.
     */
    async fetchSingleMediaType({
      mediaType,
      shouldPersistMedia,
    }: {
      mediaType: SupportedMediaType
      shouldPersistMedia: boolean
    }) {
      const queryParams = prepareSearchQueryParams({
        ...useSearchStore().searchQueryParams,
      })
      let page
      if (shouldPersistMedia) {
        /**
         * If `shouldPersistMedia` is true, then we increment the page that was set by a previous
         * fetch. Normally, if `shouldPersistMedia` is true, `page` should have been set to 1 by the
         * previous fetch. But if it wasn't and is still undefined, we set it to 0, and increment it.
         */
        page = (this.results[mediaType].page ?? 0) + 1
        queryParams.page = `${page}`
      }
      this._updateFetchState(mediaType, 'start')
      try {
        const data = await services[mediaType].search(queryParams)

        const mediaCount = data.result_count
        let errorMessage
        if (!mediaCount) {
          errorMessage = `No ${mediaType} found for this query`
          page = undefined
        }
        this._updateFetchState(mediaType, 'end', errorMessage)
        this.setMedia({
          mediaType,
          media: data.results,
          mediaCount,
          pageCount: data.page_count,
          shouldPersistMedia,
          page,
        })
      } catch (error) {
        await this.handleMediaError({ mediaType, error })
      }
    },

    async handleMediaError({
      mediaType,
      error,
    }: {
      mediaType: SupportedMediaType
      error: unknown
    }) {
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
      this._updateFetchState(mediaType, 'end', errorMessage)
      if (!axios.isAxiosError(error)) {
        throw new Error(errorMessage)
      }
    },
  },
})
