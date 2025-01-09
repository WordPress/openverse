import { expect, describe, it, beforeEach, vi } from "vitest"
import { AxiosError } from "axios"
import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"
import { image as imageObject } from "~~/test/unit/fixtures/image"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  type SupportedMediaType,
  supportedMediaTypes,
  VIDEO,
} from "#shared/constants/media"
import { NO_RESULT } from "#shared/constants/errors"
import { ON } from "#shared/constants/feature-flag"
import { deepClone } from "#shared/utils/clone"
import type { ImageDetail, Media } from "#shared/types/media"
import {
  initialResults,
  type MediaStoreResult,
  useMediaStore,
} from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"

const mocks = vi.hoisted(() => {
  return {
    createApiClient: vi.fn(),
  }
})
vi.mock("~/data/api-service", async () => {
  const actual = await vi.importActual("~/data/api-service")
  return {
    ...actual,
    createApiClient: mocks.createApiClient,
  }
})
// Retrieve the type of the first argument to
// useMediaStore.setMedia()
type SetMediaParams = Parameters<
  ReturnType<typeof useMediaStore>["setMedia"]
>[0]

const uuids = [
  "0dea3af1-27a4-4635-bab6-4b9fb76a59f5",
  "32c22b5b-f2f9-47db-b64f-6b86c2431942",
  "fd527776-00f8-4000-9190-724fc4f07346",
  "81e551de-52ab-4852-90eb-bc3973c342a0",
]
const items = (mediaType: SupportedMediaType): Media[] =>
  uuids.map((uuid, i) => ({
    id: uuid,
    title: `${mediaType} ${i + 1}`,
    creator: `creator ${i + 1}`,
    tags: [],
    sensitivity: [],
    originalTitle: `Title ${i + 1}`,
    url: "",
    foreign_landing_url: "",
    license: "by",
    license_version: "4.0",
    attribution: "",
    frontendMediaType: mediaType,
    provider: "",
    source: "",
    providerName: "",
    sourceName: "",
    detail_url: "",
    related_url: "",
    isSensitive: false,
  }))

const audioItems = items(AUDIO)
const imageItems = items(IMAGE)
const testResultItems = (mediaType: SupportedMediaType) =>
  items(mediaType).reduce<Record<string, Media>>((acc, item) => {
    acc[item.id] = item
    return acc
  }, {})

const testResult = (
  mediaType: SupportedMediaType,
  { page = 1 }: { page?: number } = {}
) =>
  ({
    count: 240,
    items: testResultItems(mediaType),
    page,
    pageCount: 20,
  }) as MediaStoreResult

const apiResult = (
  mediaType: SupportedMediaType,
  {
    count = 240,
    page = 1,
    page_count = 12,
  }: { count?: number; page?: number; page_count?: number } = {}
) => ({
  data: {
    result_count: count,
    results: count > 0 ? items(mediaType) : [],
    page,
    page_count,
  },
  eventPayload: {},
})

vi.mock("#app/nuxt", async () => {
  const original = await import("#app/nuxt")
  return {
    ...original,
    useRuntimeConfig: vi.fn(() => ({ public: { deploymentEnv: "staging" } })),
    useNuxtApp: vi.fn(() => ({
      $captureException: vi.fn(),
      $sendCustomEvent: vi.fn(),
      $processFetchingError: vi.fn(),
    })),
    tryUseNuxtApp: vi.fn(() => ({
      $config: {
        public: {
          deploymentEnv: "staging",
        },
      },
    })),
  }
})

describe("media store", () => {
  describe("state", () => {
    it("sets default state", () => {
      setActivePinia(createPinia())
      const mediaStore = useMediaStore()

      expect(mediaStore.results).toEqual({
        image: { ...initialResults },
        audio: { ...initialResults },
      })
      expect(mediaStore.mediaFetchState).toEqual({
        audio: {
          error: null,
          status: "idle",
        },
        image: {
          error: null,
          status: "idle",
        },
      })
    })
  })

  describe("getters", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
    })

    it("searchType falls back to ALL_MEDIA for additional search types", () => {
      const featureFlagStore = useFeatureFlagStore()
      featureFlagStore.toggleFeature("additional_search_types", ON)

      const searchStore = useSearchStore()
      searchStore.setSearchType(VIDEO)

      const mediaStore = useMediaStore()
      expect(mediaStore._searchType).toEqual(ALL_MEDIA)
    })

    it("getItemById returns undefined if there are no items", () => {
      const mediaStore = useMediaStore()
      expect(mediaStore.getItemById(IMAGE, "foo")).toBeUndefined()
    })

    it("getItemById returns correct item", () => {
      const mediaStore = useMediaStore()
      const expectedItem = imageItems[0]
      mediaStore.results.image.items = { foo: expectedItem }
      expect(mediaStore.getItemById(IMAGE, "foo")).toEqual(expectedItem)
    })

    it("resultItems returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results = {
        audio: testResult(AUDIO),
        image: testResult(IMAGE),
      }

      expect(mediaStore.resultItems).toEqual({
        [AUDIO]: audioItems,
        [IMAGE]: imageItems,
      })
    })

    it("allMedia returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results = {
        audio: testResult(AUDIO),
        image: testResult(IMAGE),
      }

      expect(mediaStore.allMedia).toEqual([
        imageItems[0],
        audioItems[0],
        audioItems[1],
        imageItems[1],
        imageItems[2],
        imageItems[3],
      ])
    })

    /**
     * Normally, this should randomly intersperse items from other media types.
     * Now, however, it simply returns the audio items in order.
     * TODO: Add video and check for randomization.
     */
    it("allMedia returns items even if there are no images", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)

      expect(mediaStore.allMedia).toEqual(audioItems)
    })
    it("resultCountsPerMediaType returns correct items for %s", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.image = testResult(IMAGE)

      // image is first in the returned list
      expect(mediaStore.resultCountsPerMediaType).toEqual([
        [IMAGE, testResult(IMAGE).count],
        [AUDIO, initialResults.count],
      ])
    })

    it.each`
      searchType   | count
      ${ALL_MEDIA} | ${240}
      ${AUDIO}     | ${0}
      ${IMAGE}     | ${240}
    `("resultCount for $searchType returns $count", ({ searchType, count }) => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(searchType)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.resultCount).toEqual(count)
    })

    it.each`
      fetchingMediaType | error                  | fetchState
      ${AUDIO}          | ${{ code: NO_RESULT }} | ${{ error: null, status: "fetching" }}
      ${IMAGE}          | ${null}                | ${{ error: null, status: "fetching" }}
    `(
      "fetchState for ALL_MEDIA returns `fetching` even if at least one media type is fetching",
      ({ fetchingMediaType, error, fetchState }) => {
        const mediaStore = useMediaStore()
        const searchStore = useSearchStore()
        searchStore.searchType = ALL_MEDIA
        const fetchError = error
          ? {
              requestKind: "search",
              searchType: AUDIO,
              ...error,
            }
          : null
        supportedMediaTypes.forEach((mediaType) => {
          if (mediaType === fetchingMediaType) {
            mediaStore.updateFetchState(mediaType, "start")
          } else {
            mediaStore.updateFetchState(mediaType, "end", fetchError)
          }
        })

        expect(mediaStore.fetchState).toEqual(fetchState)
      }
    )

    it("fetchState for audio returns audio error", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.searchType = AUDIO
      const error = {
        requestKind: "search",
        searchType: AUDIO,
        statusCode: 429,
        code: "ERR_UNKNOWN",
      } as const

      mediaStore.updateFetchState(AUDIO, "end", error)

      expect(mediaStore.fetchState).toEqual({ status: "error", error })
    })
    it("fetchState for image is reset after audio error", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(AUDIO)
      const error = {
        requestKind: "search",
        searchType: AUDIO,
        statusCode: 429,
        code: "ERR_UNKNOWN",
      } as const
      mediaStore.updateFetchState(AUDIO, "end", error)

      searchStore.setSearchType(IMAGE)
      mediaStore.updateFetchState(IMAGE, "start")

      expect(mediaStore.fetchState).toEqual({ status: "fetching", error: null })
    })

    it("returns NO_RESULT error if all media types have NO_RESULT errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore.updateFetchState(AUDIO, "end", {
        requestKind: "search",
        searchType: AUDIO,
        code: NO_RESULT,
      })
      mediaStore.updateFetchState(IMAGE, "end", {
        requestKind: "search",
        searchType: IMAGE,
        code: NO_RESULT,
      })

      expect(mediaStore.fetchState).toEqual({
        error: {
          requestKind: "search",
          code: NO_RESULT,
          searchType: ALL_MEDIA,
        },
        status: "error",
      })
    })

    it("fetchState for ALL_MEDIA returns no error when media types have no errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore.updateFetchState(AUDIO, "end")
      mediaStore.updateFetchState(IMAGE, "end")

      expect(mediaStore.fetchState).toEqual({
        error: null,
        status: "success",
      })
    })

    it("fetchState for ALL_MEDIA returns compound error if all types have errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)

      mediaStore.updateFetchState(AUDIO, "end", {
        code: "NO_RESULT",
        message: "Error",
        requestKind: "search",
        searchType: "audio",
        statusCode: 500,
      })

      mediaStore.updateFetchState(IMAGE, "end", {
        code: "NO_RESULT",
        message: "Error",
        requestKind: "search",
        searchType: IMAGE,
        statusCode: 500,
      })

      expect(mediaStore.fetchState).toEqual({
        error: {
          code: "NO_RESULT",
          message: "Error",
          requestKind: "search",
          searchType: ALL_MEDIA,
          statusCode: 500,
        },
        status: "error",
      })
    })
  })

  describe("actions", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
      vi.restoreAllMocks()
    })

    it("setMedia updates state persisting images", () => {
      const mediaStore = useMediaStore()

      const img1 = imageItems[0]
      const img2 = imageItems[1]

      mediaStore.results.image.items = { [img1.id]: img1 }

      const params: SetMediaParams = {
        media: { [img2.id]: img2 as ImageDetail },
        mediaCount: 2,
        page: 2,
        pageCount: 1,
        shouldPersistMedia: true,
        mediaType: IMAGE,
      }
      mediaStore.setMedia(params)

      expect(mediaStore.results.image.items).toEqual({
        [img1.id]: img1,
        [img2.id]: img2,
      })
      expect(mediaStore.results.image.count).toBe(params.mediaCount)
      expect(mediaStore.results.image.page).toBe(params.page)
    })

    it("setMedia updates state not persisting images", () => {
      const mediaStore = useMediaStore()
      const image = { ...imageObject, id: "img0" }

      const img = imageObject

      mediaStore.results.image.items = {
        ...mediaStore.results.image.items,
        image,
      }
      mediaStore.results.image.count = 10

      const params: SetMediaParams = {
        media: { [img.id]: img },
        mediaCount: 2,
        mediaType: IMAGE,
        page: 2,
        pageCount: 1,
        shouldPersistMedia: false,
      }
      mediaStore.setMedia(params)

      expect(mediaStore.results.image).toEqual({
        items: { [img.id]: img },
        count: params.mediaCount,
        page: params.page,
        pageCount: params.pageCount,
      })
    })

    it("setMedia updates state with default count and page", () => {
      const mediaStore = useMediaStore()

      const existingImg = imageItems[0]
      const img = imageItems[1]
      mediaStore.results.image.items = { [existingImg.id]: existingImg }
      const params: SetMediaParams = {
        media: { [img.id]: img },
        mediaType: IMAGE,
        shouldPersistMedia: false,
        pageCount: 1,
        mediaCount: 1,
        page: 1,
      }

      mediaStore.setMedia(params)

      expect(mediaStore.results.image.count).toEqual(1)
      expect(mediaStore.results.image.page).toEqual(1)
    })

    it("clearMedia resets the results", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()

      searchStore.setSearchType(ALL_MEDIA)

      mediaStore.results.image.items = {
        ...mediaStore.results.image.items,
        ...testResult(IMAGE).items,
      }
      mediaStore.results.audio.items = {
        ...mediaStore.results.audio.items,
        ...testResult(AUDIO).items,
      }

      mediaStore.clearMedia()

      supportedMediaTypes.forEach((mediaType) => {
        expect(mediaStore.results[mediaType]).toEqual(initialResults)
      })
    })

    it("setMediaProperties merges the existing media item together with the properties passed in allowing overwriting", () => {
      const hasLoaded = true
      const mediaStore = useMediaStore()

      mediaStore.results.audio = testResult(AUDIO)

      const existingMediaItem = deepClone(
        mediaStore.getItemById(AUDIO, uuids[0])
      )
      mediaStore.setMediaProperties(AUDIO, uuids[0], {
        hasLoaded,
      })

      expect(mediaStore.getItemById(AUDIO, uuids[0])).toMatchObject({
        ...existingMediaItem,
        hasLoaded,
      })
    })

    it("fetchMedia should fetch all supported media types from the API if search type is ALL_MEDIA", async () => {
      const searchMock = vi.fn((mediaType: SupportedMediaType) =>
        Promise.resolve(apiResult(mediaType))
      )
      mocks.createApiClient.mockImplementation(
        vi.fn(() => ({ search: searchMock }))
      )
      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")

      const mediaStore = useMediaStore()
      const media = await mediaStore.fetchMedia()

      expect(media.items.length).toEqual(6)

      expect(mocks.createApiClient).toHaveBeenCalledWith({
        accessToken: undefined,
        fakeSensitive: false,
      })

      expect(searchMock.mock.calls).toEqual([
        [IMAGE, { q: "cat" }],
        [AUDIO, { q: "cat" }],
      ])
    })

    it("fetchMedia should fetch only the specified media type from the API if search type is not ALL_MEDIA", async () => {
      const searchMock = vi.fn((mediaType: SupportedMediaType) =>
        Promise.resolve(apiResult(mediaType))
      )
      mocks.createApiClient.mockImplementation(
        vi.fn(() => ({ search: searchMock }))
      )
      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")
      searchStore.searchType = IMAGE

      const mediaStore = useMediaStore()
      const media = await mediaStore.fetchMedia()

      expect(media.items.length).toEqual(4)
      expect(searchMock).toHaveBeenCalledTimes(1)
      expect(searchMock).toHaveBeenCalledWith("image", { q: "cat" })
      expect(mediaStore.currentPage).toEqual(1)
    })

    it("fetchMedia fetches the next page of results", async () => {
      const searchMock = vi.fn((mediaType: SupportedMediaType) =>
        Promise.resolve(apiResult(mediaType, { page: 2 }))
      )
      mocks.createApiClient.mockImplementationOnce(
        vi.fn(() => ({ search: searchMock }))
      )
      const searchStore = useSearchStore()
      searchStore.searchTerm = "cat"
      searchStore.searchType = IMAGE

      const mediaStore = useMediaStore()
      mediaStore.results.image = testResult(IMAGE)
      mediaStore.mediaFetchState.image = { status: "success", error: null }

      await mediaStore.fetchMedia({ shouldPersistMedia: true })

      expect(searchMock).toHaveBeenCalledWith("image", { page: "2", q: "cat" })
      expect(mediaStore.currentPage).toEqual(2)
    })

    it("fetchMedia handles rejected promises", async () => {
      mocks.createApiClient.mockImplementationOnce(
        vi.fn(() => ({
          search: () =>
            Promise.reject(new AxiosError("Request failed", "ERR_UNKNOWN")),
        }))
      )

      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")
      searchStore.searchType = AUDIO

      const mediaStore = useMediaStore()
      mediaStore.results.audio.items = testResultItems(AUDIO)

      expect(mediaStore.results.image.items).toEqual({})
    })

    it("fetchSingleMediaType should fetch a single media from the API", async () => {
      mocks.createApiClient.mockImplementationOnce(
        vi.fn(() => ({
          search: (mediaType: SupportedMediaType) =>
            Promise.resolve(apiResult(mediaType)),
        }))
      )
      const searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")

      const mediaStore = useMediaStore()
      const media = await mediaStore.fetchSingleMediaType({
        mediaType: IMAGE,
        shouldPersistMedia: false,
      })

      expect(media).toEqual(240)
    })

    it("fetchSingleMediaType throws an error no results", async () => {
      mocks.createApiClient.mockImplementationOnce(
        vi.fn(() => ({
          search: () => Promise.resolve(apiResult(IMAGE, { count: 0 })),
        }))
      )

      const mediaStore = useMediaStore()
      await mediaStore.fetchSingleMediaType({
        mediaType: IMAGE,
        shouldPersistMedia: false,
      })

      const imageFetchState = mediaStore.mediaFetchState.image
      expect(imageFetchState).toEqual({
        status: "error",
        error: {
          code: NO_RESULT,
          details: { searchTerm: "" },
          message: "No results found for ",
          requestKind: "search",
          searchType: IMAGE,
        },
      })
    })
  })
})
