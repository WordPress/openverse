import { computed, ComputedRef, reactive } from '@nuxtjs/composition-api'
import { defineStore } from 'pinia'
import axios from 'axios'

import prepareSearchQueryParams from '~/utils/prepare-search-query-params'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedMediaTypes,
} from '~/constants/media'
import type { Media, DetailFromMediaType } from '~/models/media'
import { hash, rand as prng } from '~/utils/prng'
import { services } from '~/stores/media/services'
import { useProviderStore } from '~/stores/provider'
import { useSearchStore } from '~/stores/search'
import { FetchState, useFetchState } from '~/composables/use-fetch-state'

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
  fetchState: {
    audio: FetchState
    image: FetchState
  }
  audio: DetailFromMediaType<'audio'> | null
  image: DetailFromMediaType<'image'> | null
}

export const useMediaStore = defineStore('media', () => {
  /* State */
  /**
   * TODO: Split media store into single-type media stores.
   */
  const fetchStates = {
    [AUDIO]: useFetchState(),
    [IMAGE]: useFetchState(),
  }
  const state: MediaState = reactive({
    results: {
      [IMAGE]: {
        count: 0,
        page: undefined,
        pageCount: 0,
        items: {},
      },
      [AUDIO]: {
        count: 0,
        page: undefined,
        pageCount: 0,
        items: {},
      },
    },
    fetchState: {
      audio: fetchStates[AUDIO].fetchState,
      image: fetchStates[AUDIO].fetchState,
    },
    audio: null,
    image: null,
  })

  /* Getters */

  const getItemById = (id: string, mediaType: SupportedMediaType) => {
    return state.results[mediaType].items[id]
  }
  /**
   * Returns object with a key for each supported media type and arrays of media items for each.
   */
  const resultItems = computed(() => {
    return supportedMediaTypes.reduce(
      (items, type) => ({
        ...items,
        [type]: Object.values(state.results[type].items),
      }),
      {} as Record<SupportedMediaType, Media[]>
    )
  })
  /**
   * Returns result item counts for each supported media type.
   */
  const resultCountsPerMediaType: ComputedRef<[SupportedMediaType, number][]> =
    computed(() =>
      supportedMediaTypes.map((type) => [type, state.results[type].count])
    )
  /**
   * Returns the total count of results for selected search type, sums all media results for ALL_MEDIA.
   * If the count is more than 10000, returns 10000 to match the API result.
   */
  const resultCount = computed(() => {
    const types = (
      searchType.value === ALL_MEDIA ? supportedMediaTypes : [searchType.value]
    ) as SupportedMediaType[]
    const count = types.reduce(
      (sum, mediaType) => sum + state.results[mediaType].count,
      0
    )
    return Math.min(count, 10000)
  })
  /**
   * Search fetching state for selected search type. For 'All content', aggregates
   * the values for supported media types.
   */
  const fetchState = computed(() => {
    if (searchType.value === ALL_MEDIA) {
      /**
       * For all_media, we return the error for the first media type that has an error.
       */
      const findFirstError = () => {
        for (const type of supportedMediaTypes) {
          if (fetchStates[type].fetchState.fetchingError) {
            return fetchStates[type].fetchState.fetchingError
          }
        }
        return null
      }
      const atLeastOne = (property: keyof FetchState) =>
        supportedMediaTypes.some(
          (type) => fetchStates[type].fetchState[property]
        )

      return {
        isFetching: atLeastOne('isFetching'),
        fetchingError: findFirstError(),
        canFetch: atLeastOne('canFetch'),
        hasStarted: atLeastOne('hasStarted'),
        isFinished: supportedMediaTypes.every(
          (type) => fetchStates[type].fetchState.isFinished
        ),
      }
    } else {
      return fetchStates[searchType.value].fetchState
    }
  })
  const searchType = computed(() => useSearchStore().searchType)

  const allMedia = computed(() => {
    const media = resultItems.value

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
  })

  /* Actions */

  const setMedia = <T extends SupportedMediaType>(params: {
    mediaType: T
    media: Record<string, DetailFromMediaType<T>>
    mediaCount: number
    page: number | undefined
    pageCount: number
    shouldPersistMedia: boolean | undefined
  }) => {
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
      mediaToSet = { ...state.results[mediaType].items, ...media } as Record<
        string,
        DetailFromMediaType<T>
      >
    } else {
      mediaToSet = media
    }
    const mediaPage = page || 1
    state.results[mediaType].items = mediaToSet
    state.results[mediaType].count = mediaCount || 0
    state.results[mediaType].page = mediaCount === 0 ? undefined : mediaPage
    state.results[mediaType].pageCount = pageCount
    if (mediaPage >= pageCount) {
      fetchStates[mediaType].setFinished()
    }
  }
  const mediaNotFound = (mediaType: SupportedMediaType) => {
    throw new Error(`Media of type ${mediaType} not found`)
  }
  /**
   * Clears the items for all passed media types, and resets fetch state.
   */
  const resetMedia = (mediaType: SupportedMediaType) => {
    state.results[mediaType].items = {}
    state.results[mediaType].count = 0
    state.results[mediaType].page = undefined
    state.results[mediaType].pageCount = 0
  }
  const resetFetchState = () => {
    for (const mediaType of supportedMediaTypes) {
      fetchStates[mediaType].reset()
    }
  }

  /**
   * Calls `fetchSingleMediaType` for selected media type(s). Can be called by changing the search query
   * (search term or filter item), or by clicking 'Load more' button.
   * If the search query changed, fetch state is reset, otherwise only the media types for which
   * fetchState.isFinished is not true are fetched.
   */
  const fetchMedia = async (payload: { shouldPersistMedia?: boolean } = {}) => {
    const mediaType = searchType.value
    if (!payload.shouldPersistMedia) {
      resetFetchState()
    }
    const types = (
      mediaType !== ALL_MEDIA ? [mediaType] : [IMAGE, AUDIO]
    ) as SupportedMediaType[]
    const mediaToFetch = types.filter(
      (type) => fetchStates[type].fetchState.canFetch
    )

    await Promise.all(
      mediaToFetch.map((type) =>
        fetchSingleMediaType({
          mediaType: type,
          shouldPersistMedia: Boolean(payload.shouldPersistMedia),
        })
      )
    )
  }

  const clearMedia = () => {
    supportedMediaTypes.forEach((mediaType) => {
      resetMedia(mediaType)
    })
  }
  /**
   * @param mediaType - the mediaType to fetch (do not use 'All_media' here)
   * @param shouldPersistMedia - whether the existing media should be added to or replaced.
   */
  const fetchSingleMediaType = async ({
    mediaType,
    shouldPersistMedia,
  }: {
    mediaType: SupportedMediaType
    shouldPersistMedia: boolean
  }) => {
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
      page = (state.results[mediaType].page ?? 0) + 1
      queryParams.page = `${page}`
    }
    fetchStates[mediaType].startFetching()
    try {
      const data = await services[mediaType].search(queryParams)

      const mediaCount = data.result_count
      let errorMessage
      if (!mediaCount) {
        errorMessage = `No ${mediaType} found for this query`
        page = undefined
      }
      fetchStates[mediaType].endFetching(errorMessage)
      setMedia({
        mediaType,
        media: data.results,
        mediaCount,
        pageCount: data.page_count,
        shouldPersistMedia,
        page,
      })
    } catch (error) {
      await handleMediaError({ mediaType, error })
    }
  }
  /**
   *
   */
  const fetchMediaItem = async (params: {
    mediaType: SupportedMediaType
    id: string
  }) => {
    const { mediaType } = params
    try {
      const mediaDetail = await services[mediaType].getMediaDetail(params.id)
      const providerStore = useProviderStore()
      mediaDetail.providerName = providerStore.getProviderName(
        mediaDetail.provider,
        mediaType
      )
      if (mediaDetail.source) {
        mediaDetail.sourceName = providerStore.getProviderName(
          mediaDetail.source,
          mediaType
        )
      }
      /**
       * TODO: Fix this! Reason for disabling: TS incorrectly interprets the type of value with a
       * dynamic key as `null` instead of Media|null. Replacing with state.image solves the typing
       * error, but isn't flexible.
       */
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      state[mediaType] = mediaDetail
    } catch (error: unknown) {
      state[mediaType] = null
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        mediaNotFound(mediaType)
      } else {
        await handleMediaError({ mediaType, error })
      }
    }
  }
  /**
   *
   */
  const handleMediaError = async ({
    mediaType,
    error,
  }: {
    mediaType: SupportedMediaType
    error: unknown
  }) => {
    let errorMessage
    if (axios.isAxiosError(error)) {
      errorMessage =
        error.response?.status === 500
          ? 'There was a problem with our servers'
          : `Request failed with status ${error.response?.status ?? 'unknown'}`
    } else {
      errorMessage =
        error instanceof Error ? error.message : 'Oops! Something went wrong'
    }
    fetchStates[mediaType].endFetching(errorMessage)
    if (!axios.isAxiosError(error)) {
      throw new Error(errorMessage)
    }
  }

  return {
    state,

    getItemById,
    resultItems,
    resultCountsPerMediaType,
    resultCount,
    fetchState,
    allMedia,

    fetchSingleMediaType,
    fetchMediaItem,
    fetchMedia,
    clearMedia,

    // Elements exported only for testing, should not be used by components
    test: {
      setMedia,
      mediaNotFound,
      handleMediaError,
      fetchStates,
    },
  }
})
