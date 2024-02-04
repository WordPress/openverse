// @vitest-environment jsdom
// Using jsdom as the test environment because we need to mock axios
import { ofetch } from "ofetch"

import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { useMediaStore } from "~/stores/media"
import { AUDIO, IMAGE } from "~/constants/media"

import { DEFAULT_REQUEST_TIMEOUT } from "~/utils/query-utils"
import { useSearchStore } from "~/stores/search"

const DEFAULT_REQUEST_PARAMS = {
  timeout: DEFAULT_REQUEST_TIMEOUT,
  retry: 0,
}

const DEFAULT_ADDITIONAL_MEDIA_PARAMS = (mediaType) => ({
  creator: "",
  frontendMediaType: mediaType,
  id: 1,
  isSensitive: false,
  originalTitle: mediaType === IMAGE ? "Image" : "Audio",
  sensitivity: [],
  tags: [],
  title: mediaType === IMAGE ? "Image" : "Audio",
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
    useNuxtApp: vi.fn(() => ({
      $sentry: {
        captureException: vi.fn(),
      },
    })),
  }
})
vi.mock("ofetch", async (importOriginal) => {
  const original = await importOriginal()
  return {
    ...original,
    ofetch: {
      raw: vi.fn(() =>
        Promise.resolve({
          _data: { result_count: 10000, page: 1, page_count: 50, results: [] },
        })
      ),
    },
  }
})

vi.resetModules()

describe("fetchMedia", () => {
  beforeEach(() => {
    ofetch.raw.mockClear()
    setActivePinia(createPinia())
  })

  it("fetchMedia should fetch all supported media types from the API if search type is ALL_MEDIA", async () => {
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchMedia()

    expect(media).toEqual([])
    expect(ofetch.raw).toHaveBeenCalledTimes(2)

    // The order of calls is random, so we sort them by URL.
    const mockCallArgs = ofetch.raw.mock.calls.sort((a, b) =>
      a[0].localeCompare(b[0])
    )
    const [[audioUrl, audioParams], [imageUrl, imageParams]] = mockCallArgs
    expect(audioUrl).toEqual("/api/audio/")
    expect(imageUrl).toEqual("/api/images/")
    expect(audioParams).toEqual({
      ...DEFAULT_REQUEST_PARAMS,
      params: { q: "cat", peaks: "true" },
    })
    expect(imageParams).toEqual({
      ...DEFAULT_REQUEST_PARAMS,
      params: { q: "cat" },
    })
  })

  it("fetchMedia should fetch only the specified media type from the API if search type is not ALL_MEDIA", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: {
          result_count: 10000,
          page: 1,
          page_count: 50,
          results: items(IMAGE),
        },
      })
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = IMAGE

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchMedia()

    expect(media.length).toEqual(4)
    expect(ofetch.raw).toHaveBeenCalledTimes(1)
    expect(ofetch.raw).toHaveBeenCalledWith("/api/images/", {
      ...DEFAULT_REQUEST_PARAMS,
      params: {
        q: "cat",
      },
    })
    expect(mediaStore.currentPage).toEqual(1)
  })

  it("fetchMedia fetches the next page of results", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: {
          result_count: 10000,
          page: 1,
          page_count: 50,
          results: items(IMAGE),
        },
      })
    )
    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = IMAGE

    const mediaStore = useMediaStore()
    mediaStore.results.image = testResult(IMAGE)
    await mediaStore.fetchMedia({ shouldPersistMedia: true })

    expect(mediaStore.currentPage).toEqual(3)
    expect(ofetch.raw).toHaveBeenCalledWith("/api/images/", {
      ...DEFAULT_REQUEST_PARAMS,
      params: {
        page: "3",
        q: "cat",
      },
    })
  })

  it("fetchMedia handles rejected promises", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: { result_count: 10000, page: 1, page_count: 50, results: items },
      })
    )

    const searchStore = useSearchStore()
    searchStore.setSearchTerm("cat")
    searchStore.searchType = AUDIO

    const mediaStore = useMediaStore()
    mediaStore.results.audio.items = items(AUDIO)

    expect(mediaStore.results.image.items).toEqual({})
  })
})

describe("fetchSingleMediaType", () => {
  beforeEach(() => {
    ofetch.raw.mockClear()
    setActivePinia(createPinia())
  })

  it("fetchSingleMediaType should fetch a single media from the API", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: { result_count: 10000, page: 1, page_count: 50, results: [] },
      })
    )
    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchSingleMediaType({
      mediaType: IMAGE,
      shouldPersistMedia: false,
    })

    expect(media).toEqual(10000)
    expect(ofetch.raw).toHaveBeenCalledWith("/api/images/", {
      ...DEFAULT_REQUEST_PARAMS,
      params: {
        q: "",
      },
    })
  })

  it("fetchSingleMediaType augments item returned from the API", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: {
          result_count: 1,
          page: 1,
          page_count: 1,
          results: [{ id: 1 }],
        },
      })
    )

    const mediaStore = useMediaStore()
    const media = await mediaStore.fetchSingleMediaType({
      mediaType: IMAGE,
      shouldPersistMedia: false,
    })

    expect(media).toEqual(1)
    expect(mediaStore.results.image.items[1]).toEqual({
      creator: "",
      id: 1,
      ...DEFAULT_ADDITIONAL_MEDIA_PARAMS(IMAGE),
    })

    expect(ofetch.raw).toHaveBeenCalledWith("/api/images/", {
      params: { q: "" },
      ...DEFAULT_REQUEST_PARAMS,
    })
  })

  it("fetchSingleMediaType throws an error no results", async () => {
    ofetch.raw.mockImplementation(() =>
      Promise.resolve({
        _data: {
          result_count: 0,
          page: 1,
          page_count: 0,
          results: [],
        },
      })
    )

    const mediaStore = useMediaStore()
    await expect(async () =>
      mediaStore.fetchSingleMediaType({
        mediaType: IMAGE,
        shouldPersistMedia: false,
      })
    ).rejects.toThrowError("No results found")

    const media = mediaStore.results.image.items
    expect(Object.keys(media).length).toEqual(0)

    expect(mediaStore.fetchState).toEqual({
      fetchingError: null,
      hasStarted: true,
      isFetching: false,
      isFinished: false,
    })
  })
})
