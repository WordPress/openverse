import { defineStore } from "pinia"

import { warn } from "~/utils/console"
import { hash, rand as prng } from "~/utils/prng"
import { isRetriable, parseFetchingError } from "~/utils/errors"
import type {
  AudioDetail,
  DetailFromMediaType,
  ImageDetail,
  Media,
} from "~/types/media"
import type { FetchingError, FetchState } from "~/types/fetch-state"
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  isAdditionalSearchType,
  SupportedMediaType,
  supportedMediaTypes,
} from "~/constants/media"
import { NO_RESULT } from "~/constants/errors"
import { initServices } from "~/stores/media/services"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { deepFreeze } from "~/utils/deep-freeze"

import { PaginatedSearchQuery } from "~/types/search"

export type MediaStoreResult = {
  count: number
  pageCount: number
  page: number
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
  currentPage: number
}
export type MediaResults = {
  [MT in SupportedMediaType]: DetailFromMediaType<MT>[]
}

export const initialResults = deepFreeze({
  count: 0,
  page: 0,
  pageCount: 0,
  items: {},
}) as MediaStoreResult

export const useMediaStore = defineStore("media", {
  state: (): MediaState => ({
    results: {
      [AUDIO]: { ...initialResults },
      [IMAGE]: { ...initialResults },
    },
    mediaFetchState: {
      [AUDIO]: {
        isFetching: false,
        hasStarted: false,
        isFinished: false,
        fetchingError: null,
      },
      [IMAGE]: {
        isFetching: false,
        hasStarted: false,
        isFinished: false,
        fetchingError: null,
      },
    },
    currentPage: 0,
  }),

  getters: {
    _searchType() {
      const searchType = useSearchStore().searchType
      if (isAdditionalSearchType(searchType)) {
        return ALL_MEDIA
      }
      return searchType
    },
    /**
     * Returns a media item that exists either in the search results
     * or in the related media store.
     * This makes the single result page rendering faster by providing initial data.
     * We still need to fetch the single result from the API to get the full data.
     * @param state - the media store state
     */
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
    resultItems(state): MediaResults {
      return supportedMediaTypes.reduce(
        (items, type) => ({
          ...items,
          [type]: Object.values(state.results[type].items),
        }),
        {} as MediaResults
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
         * For all_media, we return 'All media fetching error' if all types have some kind of error.
         */
        const atLeastOne = (property: keyof FetchState) =>
          supportedMediaTypes.some(
            (type) => this.mediaFetchState[type][property]
          )

        /**
         * Returns a combined error for all media types.
         *
         * If at least one media type has a 429 error, returns 429 to stop the
         * user from retrying the request.
         *
         * If all media types have a NO_RESULT error, returns it to show the "No results" page.
         *
         * If at least one media type has a different error, returns the first error.
         * The handling of errors other than 429 should be improved after we
         * get more information about the error codes we get from the API.
         */
        const allMediaError = (): null | FetchingError => {
          const errors = getMediaErrors(this.mediaFetchState)

          if (!errors.length) {
            return null
          }

          const tooManyRequestsError = findTooManyRequestsError(errors)
          if (tooManyRequestsError !== null) {
            tooManyRequestsError["searchType"] = ALL_MEDIA
            return tooManyRequestsError
          }

          const noResultError = findNoResultError(errors)
          if (noResultError) {
            return noResultError
          }
          // Temporarily return the first error, until we have a better way to handle this.
          const results = errors.filter((error) => error.code !== NO_RESULT)
          return results.length ? results[0] : null
        }

        return {
          isFetching: atLeastOne("isFetching"),
          fetchingError: allMediaError(),
          hasStarted: atLeastOne("hasStarted"),
          isFinished: supportedMediaTypes.every(
            (type) => this.mediaFetchState[type].isFinished
          ),
        }
      } else if (isSearchTypeSupported(this._searchType)) {
        return this.mediaFetchState[this._searchType]
      } else {
        return {
          isFetching: false,
          fetchingError: null,
          hasStarted: false,
          isFinished: false,
        }
      }
    },

    /**
     * Returns a mixed bag of search results across media types.
     *
     * This does not contain all hits across all media types! It contains all
     * the hits for the media type with the most hits and as many hits from
     * other media types as can be sparsely spliced into the list. The
     * leftover hits will appear in subsequent pages.
     *
     * TODO: Fix the algorithm.
     * This implementation can hide hits from media types with fewer hits.
     */
    allMedia(state): (AudioDetail | ImageDetail)[] {
      const media = this.resultItems

      // Seed the random number generator with the ID of
      // the first search result, so the non-image
      // distribution is the same on repeated searches
      const seedString = media[IMAGE][0]?.id
      let seed: number
      if (typeof seedString === "string") {
        seed = hash(seedString)
      } else {
        let otherTypeId = "string"
        for (const type of supportedMediaTypes.slice(1)) {
          if (typeof media[type][0]?.id === "string") {
            otherTypeId = media[type][0].id
            break
          }
        }
        seed = hash(otherTypeId)
      }
      const rand = prng(seed)
      const randomIntegerInRange = (min: number, max: number) =>
        Math.floor(rand() * (max - min + 1)) + min

      // First, identify the media type with most hits
      const [mostHits] = supportedMediaTypes
        .map((type): [SupportedMediaType, number] => [
          type,
          state.results[type].count,
        ])
        .sort(([, a], [, b]) => b - a)[0]

      // First, set the results to the type with most hits...
      const newResults = media[mostHits] as (AudioDetail | ImageDetail)[]

      // ...then push other items into the list, using a random index.
      let nonImageIndex = 1
      for (const type of supportedMediaTypes.filter(
        (type) => type !== mostHits
      )) {
        for (const item of media[type]) {
          newResults.splice(nonImageIndex, 0, item)
          nonImageIndex = randomIntegerInRange(
            nonImageIndex + 1,
            nonImageIndex + 6
          )

          // Prevent the bunching of audio results at the end.
          if (nonImageIndex > newResults.length) break
        }
      }

      return newResults
    },
    _fetchableMediaTypes(): SupportedMediaType[] {
      return (
        (this._searchType !== ALL_MEDIA
          ? [this._searchType]
          : [IMAGE, AUDIO]) as SupportedMediaType[]
      ).filter(
        (type) =>
          !this.mediaFetchState[type].fetchingError &&
          !this.mediaFetchState[type].isFetching &&
          !this.mediaFetchState[type].isFinished
      )
    },
  },

  actions: {
    _startFetching(mediaType: SupportedMediaType) {
      this.mediaFetchState[mediaType].isFetching = true
      this.mediaFetchState[mediaType].hasStarted = true
      this.mediaFetchState[mediaType].isFinished = false
      this.mediaFetchState[mediaType].fetchingError = null
    },
    /**
     * Called when the request is finished, regardless of whether it was successful or not.
     * @param mediaType - The media type for which the request was made.
     * @param error - The string representation of the error, if any.
     */
    _endFetching(mediaType: SupportedMediaType, error?: FetchingError) {
      this.mediaFetchState[mediaType].fetchingError = error || null
      this.mediaFetchState[mediaType].hasStarted = true
      this.mediaFetchState[mediaType].isFetching = false

      if (error && !isRetriable(error)) {
        this.mediaFetchState[mediaType].isFinished = true
      }
    },
    /**
     * This is called when there are no more results available in the API for specific query.
     * @param mediaType - The media type for which the request was made.
     */
    _finishFetchingForQuery(mediaType: SupportedMediaType) {
      this.mediaFetchState[mediaType].isFinished = true
      this.mediaFetchState[mediaType].hasStarted = true
      this.mediaFetchState[mediaType].isFetching = false
    },

    _resetFetchState() {
      for (const mediaType of supportedMediaTypes) {
        this.mediaFetchState[mediaType].isFetching = false
        this.mediaFetchState[mediaType].hasStarted = false
        this.mediaFetchState[mediaType].isFinished = false
        this.mediaFetchState[mediaType].fetchingError = null
      }
    },

    _updateFetchState(
      mediaType: SupportedMediaType,
      action: "reset" | "start" | "end" | "finish",
      error?: FetchingError
    ) {
      switch (action) {
        case "reset":
          this._resetFetchState()
          break
        case "start":
          this._startFetching(mediaType)
          break
        case "end":
          this._endFetching(mediaType, error)
          break
        case "finish":
          this._finishFetchingForQuery(mediaType)
          break
      }
    },

    setMedia<T extends SupportedMediaType>(params: {
      mediaType: T
      media: Record<string, DetailFromMediaType<T>>
      mediaCount: number
      page: number
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
      this.results[mediaType].page = mediaCount === 0 ? 0 : mediaPage
      this.results[mediaType].pageCount = pageCount
      if (mediaPage >= pageCount) {
        this._updateFetchState(mediaType, "finish")
      }
    },

    /**
     * Clears the items for all passed media types, and resets fetch state.
     */
    resetMedia(mediaType: SupportedMediaType) {
      this.results[mediaType].items = {}
      this.results[mediaType].count = 0
      this.results[mediaType].page = 0
      this.results[mediaType].pageCount = 0
    },

    /**
     * Calls `fetchSingleMediaType` for selected media type(s).
     * Can be called by changing the search query
     * (search term or filter item), or by clicking 'Load more' button.
     * If the search query changed, fetch state is reset, otherwise only the media types for which
     * fetchState.isFinished is not true are fetched.
     */
    async fetchMedia(payload: { shouldPersistMedia?: boolean } = {}) {
      const mediaType = this._searchType
      const shouldPersistMedia = Boolean(payload.shouldPersistMedia)
      if (!shouldPersistMedia) {
        this.clearMedia()
      }

      const mediaToFetch = this._fetchableMediaTypes

      const resultCounts = await Promise.all(
        mediaToFetch.map((mediaType) =>
          this.fetchSingleMediaType({ mediaType, shouldPersistMedia })
        )
      )
      const resultCount = resultCounts.includes(null)
        ? null
        : (resultCounts as number[]).reduce((a, b) => a + b, 0)

      this.currentPage =
        mediaType === ALL_MEDIA
          ? this.currentPage + 1
          : this.results[mediaType].page
      return resultCount
    },

    clearMedia() {
      supportedMediaTypes.forEach((mediaType) => {
        this.resetMedia(mediaType)
        this._resetFetchState()
      })
      this.currentPage = 0
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
      let page = this.results[mediaType].page + 1
      const queryParams: PaginatedSearchQuery = {
        ...useSearchStore().apiSearchQueryParams,
        // Don't need to set `page` parameter for the first page.
        page: shouldPersistMedia ? `${page}` : undefined,
      }

      this._updateFetchState(mediaType, "start")
      try {
        const accessToken = this.$nuxt.$openverseApiToken
        const service = initServices[mediaType](accessToken)
        const data = await service.search(queryParams)
        const mediaCount = data.result_count
        let errorData: FetchingError | undefined
        /**
         * When there are no results for a query, the API returns a 200 response.
         * In such cases, we show the "No results" client error page.
         */
        if (!mediaCount) {
          page = 1
          errorData = {
            message: `No results found for ${queryParams.q}`,
            code: NO_RESULT,
            requestKind: "search",
            searchType: mediaType,
            details: { searchTerm: queryParams.q ?? "" },
          }
        }
        this._updateFetchState(mediaType, "end", errorData)

        this.setMedia({
          mediaType,
          media: data.results,
          mediaCount,
          pageCount: data.page_count,
          shouldPersistMedia,
          page,
        })
        return mediaCount
      } catch (error: unknown) {
        const errorData = parseFetchingError(error, mediaType, "search", {
          searchTerm: queryParams.q ?? "",
        })

        this._updateFetchState(mediaType, "end", errorData)

        this.$nuxt.$sentry.captureException(error, {
          extra: { errorData },
        })
        return null
      }
    },

    setMediaProperties(
      type: SupportedMediaType,
      id: string,
      properties: Partial<DetailFromMediaType<typeof type>>
    ) {
      const item = this.getItemById(type, id)
      if (item) {
        Object.assign(item, properties)
      } else {
        warn(
          `Attempted to update media item ${type} ${id} but could not find it.`
        )
      }
    },
  },
})

const getMediaErrors = (mediaFetchStates: MediaState["mediaFetchState"]) => {
  return supportedMediaTypes
    .map((mediaType) => mediaFetchStates[mediaType].fetchingError)
    .filter((err): err is FetchingError => err !== null)
}

const findTooManyRequestsError = (errors: FetchingError[]) => {
  return errors.find(({ statusCode }) => statusCode === 429) ?? null
}

const findNoResultError = (errors: FetchingError[]): FetchingError | null => {
  return errors.length === supportedMediaTypes.length &&
    errors.every(({ code }) => code === NO_RESULT)
    ? { ...errors[0], searchType: ALL_MEDIA }
    : null
}
