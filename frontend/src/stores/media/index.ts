import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  isAdditionalSearchType,
  SupportedMediaType,
  supportedMediaTypes,
} from "#shared/constants/media"
import { NO_RESULT } from "#shared/constants/errors"
import { hash, rand as prng } from "#shared/utils/prng"
import { deepFreeze } from "#shared/utils/deep-freeze"
import type {
  AudioDetail,
  DetailFromMediaType,
  ImageDetail,
  Media,
} from "#shared/types/media"
import type { FetchingError, FetchState } from "#shared/types/fetch-state"
import type { Results } from "#shared/types/result"
import { warn } from "~/utils/console"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useApiClient } from "~/composables/use-api-client"

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

const areMorePagesAvailable = ({
  page,
  pageCount,
}: {
  page: number
  pageCount: number
}) => {
  return page < pageCount
}

export const useMediaStore = defineStore("media", {
  state: (): MediaState => ({
    results: {
      [AUDIO]: { ...initialResults },
      [IMAGE]: { ...initialResults },
    },
    mediaFetchState: {
      [AUDIO]: { status: "idle", error: null },
      [IMAGE]: { status: "idle", error: null },
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
        if (itemFromSearchResults) {
          return itemFromSearchResults
        }
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
     */
    resultCount(state) {
      const types = (
        this._searchType === ALL_MEDIA ||
        !isSearchTypeSupported(this._searchType)
          ? supportedMediaTypes
          : [this._searchType]
      ) as SupportedMediaType[]
      return types.reduce(
        (sum, mediaType) => sum + state.results[mediaType].count,
        0
      )
    },

    /**
     * Search fetching state for selected search type. For 'All content', aggregates
     * the values for supported media types:
     * - show fetching state if any of the media types is fetching, even if one of the
     * media types has an error.
     * - show idle state if all media types are idle.
     * - show error state if any of the media types has an error.
     * - show success state if all media types are successful, and idle - otherwise.
     */
    fetchState(): FetchState {
      if (this._searchType === ALL_MEDIA) {
        const statuses = supportedMediaTypes.map(
          (type) => this.mediaFetchState[type].status
        )
        if (statuses.includes("fetching")) {
          return { status: "fetching", error: null }
        }
        if (statuses.every((s) => s === "idle")) {
          return { status: "idle", error: null }
        }
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

        const error = allMediaError()
        if (error) {
          return { status: "error", error }
        }
        return {
          status: statuses.includes("idle") ? "idle" : "success",
          error: null,
        }
      } else if (isSearchTypeSupported(this._searchType)) {
        return this.mediaFetchState[this._searchType]
      } else {
        return { status: "idle", error: null }
      }
    },

    isFetching(): boolean {
      return this.fetchState.status === "fetching"
    },

    showLoading(): boolean {
      console.log("show loading", this.fetchState.status, this.currentPage)
      return (
        this.fetchState.status === "idle" ||
        (this.fetchState.status === "fetching" && this.currentPage < 2)
      )
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
          if (nonImageIndex > newResults.length) {
            break
          }
        }
      }

      return newResults
    },

    /**
     * Returns an array of media types that can be fetched:
     *  - current media type, or all media types if the search type is ALL_MEDIA
     *  - are not currently fetching and don't have error
     *  - either the first page has not been fetched yet, or there are more pages available
     */
    _fetchableMediaTypes(): SupportedMediaType[] {
      return (
        (this._searchType !== ALL_MEDIA
          ? [this._searchType]
          : [IMAGE, AUDIO]) as SupportedMediaType[]
      ).filter((type) => {
        if (!["idle", "success"].includes(this.mediaFetchState[type].status)) {
          return false
        }
        // Either the first page has not been fetched yet, or there are more pages available.
        return (
          this.results[type].page < 1 ||
          areMorePagesAvailable(this.results[type])
        )
      })
    },

    /**
     * Returns the search results array for the current search type.
     */
    searchResults(): Results {
      const searchType = this._searchType

      if (searchType === ALL_MEDIA) {
        return { type: ALL_MEDIA, items: [...this.allMedia] } as const
      } else if (searchType === IMAGE) {
        return { type: IMAGE, items: this.resultItems[IMAGE] } as const
      } else {
        return { type: AUDIO, items: this.resultItems[AUDIO] } as const
      }
    },

    /**
     * Used to display the load more button in the UI.
     * For all the media types that can be fetched for the current search type
     * (i.e., `image` for `image`, or [`image`, `audio`] for `ALL_MEDIA`), checks
     * that the first page of the results has been fetched and that the API has more pages.
     */
    canLoadMore(): boolean {
      const types = this._fetchableMediaTypes
      return (
        types.length > 0 &&
        types.every((type) => this.results[type].pageCount !== 0)
      )
    },
  },

  actions: {
    _startFetching(mediaType: SupportedMediaType) {
      this.mediaFetchState[mediaType] = { status: "fetching", error: null }
    },

    /**
     * Called when the request is finished, regardless of whether it was successful or not.
     * @param mediaType - The media type for which the request was made.
     * @param error - The string representation of the error, if any.
     */
    _endFetching(mediaType: SupportedMediaType, error?: FetchingError) {
      if (error) {
        this.mediaFetchState[mediaType] = { status: "error", error }
      } else {
        this.mediaFetchState[mediaType] = { status: "success", error: null }
      }
    },

    _resetFetchState() {
      for (const mediaType of supportedMediaTypes) {
        this.mediaFetchState[mediaType] = { status: "idle", error: null }
      }
    },

    updateFetchState(
      mediaType: SupportedMediaType,
      action: "reset" | "start" | "end",
      error?: FetchingError
    ) {
      switch (action) {
        case "reset": {
          this._resetFetchState()
          break
        }
        case "start": {
          this._startFetching(mediaType)
          break
        }
        case "end": {
          this._endFetching(mediaType, error)
          break
        }
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
        mediaCount: count,
        page,
        pageCount,
        shouldPersistMedia,
      } = params
      let items

      if (shouldPersistMedia) {
        items = { ...this.results[mediaType].items, ...media } as Record<
          string,
          DetailFromMediaType<T>
        >
      } else {
        items = media
      }

      // Edge case when the dead link filtering removed all results from subsequent pages:
      // set the pageCount and the count to the current values.
      if (page > 1 && count === 0) {
        this.results[mediaType] = {
          items,
          count: Object.keys(items).length,
          page: page - 1,
          pageCount: page - 1,
        }
      } else {
        this.results[mediaType] = {
          items,
          count,
          page,
          pageCount,
        }
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
     * Fetches the selected media types.
     * If the search query changed, fetch state is reset, otherwise only the media types for which
     * fetchState.isFinished is not true are fetched.
     */
    async fetchMedia(
      payload: { shouldPersistMedia?: boolean } = {}
    ): Promise<Results> {
      const shouldPersistMedia = Boolean(payload.shouldPersistMedia)

      await Promise.allSettled(
        this._fetchableMediaTypes.map((mediaType) =>
          this.fetchSingleMediaType({ mediaType, shouldPersistMedia })
        )
      )

      return this.searchResults
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
      const searchStore = useSearchStore()
      const queryParams = searchStore.getApiRequestQuery(mediaType)
      let page = this.results[mediaType].page + 1

      if (shouldPersistMedia) {
        queryParams.page = `${page}`
      }

      this.updateFetchState(mediaType, "start")

      const { $sendCustomEvent, $processFetchingError } = useNuxtApp()

      const client = useApiClient()

      try {
        const { eventPayload, data } = await client.search(
          mediaType,
          queryParams
        )

        if (eventPayload) {
          $sendCustomEvent("SEARCH_RESPONSE_TIME", eventPayload)
        }
        const mediaCount = data.result_count
        let errorData: FetchingError | undefined

        if (page == 1) {
          $sendCustomEvent("GET_SEARCH_RESULTS", {
            ...searchStore.searchParamsForEvent,
            mediaType,
            resultsCount: mediaCount,
          })
        }

        /**
         * When there are no results for a query, the API returns a 200 response.
         * In such cases, we show the "No results" client error page.
         */
        if (!mediaCount && page < 2) {
          page = 1
          errorData = {
            message: `No results found for ${queryParams.q}`,
            code: NO_RESULT,
            requestKind: "search",
            searchType: mediaType,
            details: { searchTerm: queryParams.q ?? "" },
          }
        }
        this.updateFetchState(mediaType, "end", errorData)

        this.setMedia({
          mediaType,
          media: data.results,
          mediaCount,
          pageCount: data.page_count,
          shouldPersistMedia,
          page,
        })

        this.currentPage = page
        return mediaCount
      } catch (error: unknown) {
        const errorData = $processFetchingError(error, mediaType, "search", {
          searchTerm: queryParams.q ?? "",
        })

        this.updateFetchState(mediaType, "end", errorData)

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
    .map((mediaType) => mediaFetchStates[mediaType].error)
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
