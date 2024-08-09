// @vitest-environment jsdom
import { AxiosError } from "axios"

import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { useMediaStore } from "~/stores/media"
import { AUDIO, IMAGE } from "~/constants/media"

import { useSearchStore } from "~/stores/search"

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

vi.mock("#app/nuxt", async () => {
  const original = await import("#app/nuxt")
  return {
    ...original,
    useRuntimeConfig: vi.fn(() => ({ public: { deploymentEnv: "staging" } })),
    useNuxtApp: vi.fn(() => ({
      $sentry: {
        captureException: vi.fn(),
      },
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

describe("fetchMedia", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    mocks.createApiClient.mockRestore()
  })

  it("fetchMedia should fetch all supported media types from the API if search type is ALL_MEDIA", async () => {
    const imageSearchMock = vi.fn(() =>
      Promise.resolve({ data: { results: [] }, eventPayload: {} })
    )
    const audioSearchMock = vi.fn(() =>
      Promise.resolve({ data: { results: [] }, eventPayload: {} })
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: imageSearchMock }))
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: audioSearchMock }))
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchMedia()

    expect(media).toEqual([])
    expect(mocks.createApiClient).toHaveBeenCalledTimes(2)
    expect(imageSearchMock).toHaveBeenCalledTimes(1)

    expect(mocks.createApiClient).toHaveBeenCalledWith({
      accessToken: undefined,
    })
    expect(imageSearchMock).toHaveBeenCalledWith(IMAGE, { q: "cat" })
    expect(audioSearchMock).toHaveBeenCalledWith(AUDIO, { q: "cat" })
  })

  it("fetchMedia should fetch only the specified media type from the API if search type is not ALL_MEDIA", async () => {
    const searchMock = vi.fn(() =>
      Promise.resolve({
        data: {
          result_count: 10000,
          page: 1,
          page_count: 50,
          results: items(IMAGE),
        },
        eventPayload: {},
      })
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: searchMock }))
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = IMAGE

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchMedia()

    expect(media.length).toEqual(4)
    expect(searchMock).toHaveBeenCalledTimes(1)
    expect(searchMock).toHaveBeenCalledWith("image", { q: "cat" })
    expect(mediaStore.currentPage).toEqual(1)
  })

  it("fetchMedia fetches the next page of results", async () => {
    const searchMock = vi.fn(() =>
      Promise.resolve({
        data: {
          result_count: 10000,
          page: 1,
          page_count: 50,
          results: items(IMAGE),
        },
        eventPayload: {},
      })
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: searchMock }))
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = IMAGE

    const mediaStore = useMediaStore()
    mediaStore.results.image = testResult(IMAGE)
    await mediaStore.fetchMedia({ shouldPersistMedia: true })

    expect(mediaStore.currentPage).toEqual(3)
    expect(searchMock).toHaveBeenCalledWith("image", { page: "3", q: "cat" })
  })

  it("fetchMedia handles rejected promises", async () => {
    const searchMock = vi.fn(() =>
      Promise.reject(new AxiosError("Request failed", {}))
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: searchMock }))
    )

    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = AUDIO

    const mediaStore = useMediaStore()
    mediaStore.results.audio.items = items(AUDIO)

    expect(mediaStore.results.image.items).toEqual({})
  })

  it("fetchSingleMediaType should fetch a single media from the API", async () => {
    const searchMock = vi.fn(() =>
      Promise.resolve({
        data: { result_count: 10000, page: 1, page_count: 50, results: [] },
        eventPayload: {},
      })
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: searchMock }))
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchSingleMediaType({
      mediaType: IMAGE,
      shouldPersistMedia: false,
    })

    expect(media).toEqual(10000)
  })

  it("fetchSingleMediaType throws an error no results", async () => {
    const searchMock = vi.fn(() =>
      Promise.resolve({ data: { result_count: 0 }, eventPayload: {} })
    )
    mocks.createApiClient.mockImplementationOnce(
      vi.fn(() => ({ search: searchMock }))
    )

    const mediaStore = useMediaStore()
    await mediaStore.fetchSingleMediaType({
      mediaType: IMAGE,
      shouldPersistMedia: false,
    })

    expect(mediaStore.fetchState).toEqual({
      fetchingError: null,
      hasStarted: true,
      isFetching: false,
      isFinished: false,
    })
  })
})
