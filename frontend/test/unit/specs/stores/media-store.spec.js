import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

import { deepClone } from "~/utils/clone"

import { initialResults, useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { ALL_MEDIA, AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"

const uuids = [
  "0dea3af1-27a4-4635-bab6-4b9fb76a59f5",
  "32c22b5b-f2f9-47db-b64f-6b86c2431942",
  "fd527776-00f8-4000-9190-724fc4f07346",
  "81e551de-52ab-4852-90eb-bc3973c342a0",
]
const items = (mediaType) =>
  uuids.map((uuid, i) => ({
    id: uuid,
    title: `${mediaType} ${i + 1}`,
    creator: `creator ${i + 1}`,
    tags: [],
  }))

const audioItems = items(AUDIO)
const imageItems = items(IMAGE)
const testResultItems = (mediaType) =>
  items(mediaType).reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {})

const testResult = (mediaType) => ({
  count: 10001,
  items: testResultItems(mediaType),
  page: 2,
  pageCount: 20,
})

const searchResults = (mediaType) => ({
  results: testResultItems(mediaType),
  result_count: 22,
  page_count: 2,
})

const mockImplementation = (mediaType) => () =>
  Promise.resolve({
    searchTimeEvent: undefined,
    data: { ...searchResults(mediaType) },
  })
const mockSearchAudio = jest.fn().mockImplementation(mockImplementation(AUDIO))
const mockSearchImage = jest.fn().mockImplementation(mockImplementation(IMAGE))
const mockGetMediaDetail = jest.fn()
jest.mock("~/stores/media/services", () => ({
  initServices: {
    audio: () =>
      /** @type {typeof import('~/data/services').MediaService} */ ({
        search: mockSearchAudio,
        getMediaDetail: mockGetMediaDetail,
      }),
    image: () =>
      /** @type {typeof import('~/data/services').MediaService} */ ({
        search: mockSearchImage,
        getMediaDetail: mockGetMediaDetail,
      }),
  },
}))

describe("Media Store", () => {
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
          fetchingError: null,
          hasStarted: false,
          isFetching: false,
          isFinished: false,
        },
        image: {
          fetchingError: null,
          hasStarted: false,
          isFetching: false,
          isFinished: false,
        },
      })
    })
  })

  describe("getters", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
    })
    it("getItemById returns undefined if there are no items", () => {
      const mediaStore = useMediaStore()
      expect(mediaStore.getItemById(IMAGE, "foo")).toBe(undefined)
    })
    it("getItemById returns correct item", () => {
      const mediaStore = useMediaStore()
      const expectedItem = { id: "foo", title: "ImageFoo" }
      mediaStore.results.image.items = { foo: expectedItem }
      expect(mediaStore.getItemById(IMAGE, "foo")).toEqual(expectedItem)
    })

    it("resultItems returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.resultItems).toEqual({
        [AUDIO]: audioItems,
        [IMAGE]: imageItems,
      })
    })
    it("allMedia returns correct items", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)
      mediaStore.results.image = testResult(IMAGE)

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

      expect(mediaStore.allMedia).toEqual([
        audioItems[0],
        audioItems[1],
        audioItems[2],
        audioItems[3],
      ])
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
      ${ALL_MEDIA} | ${10000}
      ${AUDIO}     | ${0}
      ${IMAGE}     | ${10000}
    `("resultCount for $searchType returns $count", ({ searchType, count }) => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(searchType)
      mediaStore.results.image = testResult(IMAGE)

      expect(mediaStore.resultCount).toEqual(count)
    })

    it.each`
      searchType   | fetchState
      ${ALL_MEDIA} | ${{ fetchingError: { requestKind: "search", statusCode: 429, searchType: ALL_MEDIA }, hasStarted: true, isFetching: true, isFinished: false }}
      ${AUDIO}     | ${{ fetchingError: { requestKind: "search", statusCode: 429, searchType: AUDIO }, hasStarted: true, isFetching: false, isFinished: true }}
      ${IMAGE}     | ${{ fetchingError: null, hasStarted: true, isFetching: true, isFinished: false }}
    `(
      "fetchState for $searchType returns $fetchState",
      ({ searchType, fetchState }) => {
        const mediaStore = useMediaStore()
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        mediaStore._updateFetchState(AUDIO, "end", {
          requestKind: "search",
          statusCode: 429,
          searchType: AUDIO,
        })
        mediaStore._updateFetchState(IMAGE, "start")

        expect(mediaStore.fetchState).toEqual(fetchState)
      }
    )
    it("fetchState for ALL_MEDIA returns compound error if all types have errors", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore._updateFetchState(AUDIO, "end", {
        message: "Error",
        statusCode: 500,
      })
      mediaStore._updateFetchState(IMAGE, "end", {
        message: "Error",
        statusCode: 500,
        requestKind: "search",
        searchType: IMAGE,
      })

      expect(mediaStore.fetchState).toEqual({
        fetchingError: {
          message: "Error",
          statusCode: 500,
          requestKind: "search",
          searchType: IMAGE,
        },
        hasStarted: true,
        isFetching: false,
        isFinished: true,
      })
    })
  })

  describe("actions", () => {
    let searchStore

    beforeEach(() => {
      setActivePinia(createPinia())
    })
    afterEach(() => {
      mockSearchAudio.mockClear()
      mockSearchImage.mockClear()
      mockGetMediaDetail.mockClear()
    })

    it("setMedia updates state persisting images", () => {
      const mediaStore = useMediaStore()

      const img1 = {
        id: "81e551de-52ab-4852-90eb-bc3973c342a0",
        title: "Foo",
        creator: "foo",
        tags: [],
      }
      const img2 = {
        id: "0dea3af1-27a4-4635-bab6-4b9fb76a59f5",
        title: "Bar",
        creator: "bar",
        tags: [],
      }
      mediaStore.results.image.items = { [img1.id]: img1 }
      const params = {
        media: { [img2.id]: img2 },
        mediaCount: 2,
        page: 2,
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
      const img = { title: "Foo", creator: "bar", tags: [] }
      mediaStore.results.image.items = ["img1"]
      const params = {
        media: [img],
        mediaCount: 2,
        page: 2,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      mediaStore.setMedia(params)

      expect(mediaStore.results.image).toEqual({
        items: [img],
        count: params.mediaCount,
        page: params.page,
      })
    })

    it("setMedia updates state with default count and page", () => {
      const mediaStore = useMediaStore()

      const img = { title: "Foo", creator: "bar", tags: [] }
      mediaStore.results.image.items = ["img1"]
      const params = { media: [img], mediaType: IMAGE }

      mediaStore.setMedia(params)

      expect(mediaStore.results.image.count).toBe(0)
      expect(mediaStore.results.image.page).toBe(1)
    })

    it.each(supportedMediaTypes)(
      "fetchSingleMediaType (%s) on success",
      async (mediaType) => {
        const mediaStore = useMediaStore()

        searchStore = useSearchStore()
        searchStore.setSearchTerm("cat")
        const params = {
          shouldPersistMedia: true,
          mediaType,
        }
        const expectedApiResult = searchResults(mediaType)
        await mediaStore.fetchSingleMediaType(params)
        const expectedResult = {
          items: expectedApiResult.results,
          count: expectedApiResult.result_count,
          page: 1,
          pageCount: expectedApiResult.page_count,
        }
        const actualResult = mediaStore.results[mediaType]
        expect(actualResult).toEqual(expectedResult)
      }
    )
    it("fetchSingleMediaType on no results", async () => {
      const mediaStore = useMediaStore()

      searchStore = useSearchStore()
      searchStore.setSearchTerm("cat")
      const params = {
        shouldPersistMedia: true,
        mediaType: IMAGE,
      }
      const emptyResult = {
        searchTimeEvent: undefined,
        data: { result_count: 0, page_count: 0, results: [] },
      }
      mockSearchImage.mockResolvedValueOnce(emptyResult)
      await mediaStore.fetchSingleMediaType(params)

      const actualResult = mediaStore.results[IMAGE]
      expect(actualResult).toEqual({
        items: {},
        count: 0,
        page: 0,
        pageCount: 0,
      })

      expect(mediaStore.mediaFetchState["image"].fetchingError).toEqual({
        code: "NO_RESULT",
        details: { searchTerm: "cat" },
        message: "No results found for cat",
        requestKind: "search",
        searchType: "image",
      })
    })

    it("fetchSingleMediaType resets images if shouldPersistMedia is false", async () => {
      const mediaStore = useMediaStore()

      const mediaType = IMAGE
      const params = {
        shouldPersistMedia: false,
        mediaType,
      }
      const expectedResult = searchResults(mediaType)
      await mediaStore.fetchSingleMediaType(params)
      expect(mediaStore.results[mediaType]).toEqual({
        count: expectedResult.result_count,
        items: expectedResult.results,
        page: 1,
        pageCount: expectedResult.page_count,
      })
    })

    it("fetchSingleMediaType does not reset images if shouldPersistMedia is true", async () => {
      const mediaStore = useMediaStore()
      const img1 = {
        id: "123",
        frontendMediaType: "image",
        title: "Foo",
        creator: "bar",
        tags: [],
      }
      mediaStore.$patch({
        results: {
          image: {
            page: 1,
            count: 1,
            pageCount: 10,
          },
        },
      })
      mediaStore.$patch((state) => {
        state.results.image.items = { 123: img1 }
      })

      const mediaType = IMAGE
      const params = {
        q: "foo",
        page: 1,
        shouldPersistMedia: true,
        mediaType,
      }
      await mediaStore.fetchSingleMediaType(params)
      const results = mediaStore.results[mediaType]
      expect(results.items["123"]).toEqual(img1)
      expect(results.page).toBe(2)
    })

    it("clearMedia resets the results", () => {
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      searchStore.setSearchType(ALL_MEDIA)
      mediaStore.fetchMedia()
      mediaStore.clearMedia()
      supportedMediaTypes.forEach((mediaType) => {
        expect(mediaStore.results[mediaType]).toEqual(initialResults)
      })
    })

    it("setMediaProperties merges the existing media item together with the properties passed in allowing overwriting", () => {
      const mediaStore = useMediaStore()
      mediaStore.results.audio = testResult(AUDIO)

      const existingMediaItem = deepClone(
        mediaStore.getItemById(AUDIO, uuids[0])
      )
      const hasLoaded = Symbol()
      mediaStore.setMediaProperties(AUDIO, uuids[0], {
        hasLoaded,
      })

      expect(mediaStore.getItemById(AUDIO, uuids[0])).toMatchObject({
        ...existingMediaItem,
        hasLoaded,
      })
    })
  })
})
