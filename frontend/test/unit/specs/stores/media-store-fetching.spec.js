// @vitest-environment jsdom
import { setActivePinia, createPinia } from "~~/test/unit/test-utils/pinia"

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
const testResultItems = (mediaType) =>
  items(mediaType).reduce((acc, item) => {
    acc[item.id] = item
    return acc
  }, {})

const testResult = (mediaType) => ({
  count: 22,
  items: testResultItems(mediaType),
  page: 1,
  pageCount: 2,
})
const searchResults = (mediaType) => ({
  results: testResultItems(mediaType),
  result_count: 22,
  page_count: 2,
  page: 1,
})

const mockImplementation = (mediaType) => () =>
  Promise.resolve({ ...searchResults(mediaType) })
const mockSearchAudio = vi.fn().mockImplementation(mockImplementation(AUDIO))
const mockSearchImage = vi.fn().mockImplementation(mockImplementation(IMAGE))
const mockGetMediaDetail = vi.fn()
vi.mock("~/stores/media/services", () => ({
  initServices: {
    audio: () => ({
      search: mockSearchAudio,
      getMediaDetail: mockGetMediaDetail,
    }),
    image: () => ({
      search: mockSearchImage,
      getMediaDetail: mockGetMediaDetail,
    }),
  },
}))

describe("media store", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it("fetchMedia", async () => {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    searchStore.setSearchType(ALL_MEDIA)
    mockSearchImage.mockResolvedValueOnce(searchResults(IMAGE))
    mockSearchAudio.mockResolvedValueOnce(searchResults(AUDIO))

    await mediaStore.fetchMedia()
    supportedMediaTypes.forEach((mediaType) => {
      expect(mediaStore.results[mediaType]).toEqual(testResult(mediaType))
    })
  })

  it("fetchSingleMediaType on no results", async () => {
    const mediaStore = useMediaStore()

    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    const params = {
      shouldPersistMedia: true,
      mediaType: IMAGE,
      accessToken: undefined,
    }
    const emptyResult = { result_count: 0, page_count: 0, results: [] }
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
      accessToken: undefined,
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
      accessToken: "foo",
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
})
