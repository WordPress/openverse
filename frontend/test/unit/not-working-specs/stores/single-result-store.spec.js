import { AxiosError } from "axios"

import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { image as imageObj } from "~~/test/unit/fixtures/image"

import { AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"
import { useMediaStore } from "~/stores/media"
import { useSingleResultStore } from "~/stores/media/single-result"

const detailData = {
  [AUDIO]: {
    ...getAudioObj(),
    title: "audioDetails",
    id: "audio1",
    frontendMediaType: AUDIO,
  },
  [IMAGE]: {
    ...imageObj,
    title: "imageDetails",
    id: "image1",
    frontendMediaType: IMAGE,
  },
}
vi.mock("axios", async () => {
  const actualAxios = await import("axios")
  const isAxiosError = vi.fn((obj) => "response" in obj)
  return {
    ...actualAxios,
    isAxiosError,
  }
})

const mockImplementation = (mediaType) => () =>
  Promise.resolve(detailData[mediaType])
const mockGetMediaDetailAudio = vi
  .fn()
  .mockImplementation(mockImplementation(AUDIO))
const mockGetMediaDetailImage = vi
  .fn()
  .mockImplementation(mockImplementation(IMAGE))
const mocks = {
  audio: mockGetMediaDetailAudio,
  image: mockGetMediaDetailImage,
}
vi.mock("~/stores/media/services", () => ({
  initServices: {
    audio: () =>
      /** @type {import('~/data/services').MediaService} */ ({
        getMediaDetail: mockGetMediaDetailAudio,
      }),
    image: () =>
      /** @type {import('~/data/services').MediaService} */ ({
        getMediaDetail: mockGetMediaDetailImage,
      }),
  },
}))

describe("Media Item Store", () => {
  let singleResultStore = null
  let mediaStore = null
  const originalEnv = process.env

  beforeEach(() => {
    setActivePinia(createPinia())
    singleResultStore = useSingleResultStore()
    mediaStore = useMediaStore()
  })
  afterEach(() => {
    mockGetMediaDetailAudio.mockClear()
    mockGetMediaDetailImage.mockClear()
    process.env = originalEnv
  })
  describe("state", () => {
    it("sets default state", () => {
      expect(singleResultStore.fetchState).toEqual({
        isFetching: false,
        fetchingError: null,
      })
      expect(singleResultStore.mediaItem).toEqual(null)
      expect(singleResultStore.mediaType).toEqual(null)
    })
  })

  describe("getters", () => {
    it.each(supportedMediaTypes)(
      "%s getter returns the item when current item type matches",
      (mediaType) => {
        singleResultStore.$patch({
          mediaItem: detailData[mediaType],
          mediaType,
          mediaId: detailData[mediaType].id,
        })
        expect(singleResultStore[mediaType]).toEqual(detailData[mediaType])
      }
    )

    it.each(supportedMediaTypes)(
      "`%s` returns `null` if the media type doesn't match",
      (mediaType) => {
        singleResultStore.$patch({
          mediaItem: detailData[mediaType],
          mediaType: mediaType,
          mediaId: detailData[mediaType].id,
        })
        expect(
          singleResultStore[mediaType === "image" ? "audio" : "image"]
        ).toEqual(null)
      }
    )
  })

  describe("actions", () => {
    it.each(supportedMediaTypes)(
      "setMediaItem (%s) sets the media item and media type",
      (type) => {
        const mediaItem = detailData[type]
        singleResultStore.setMediaItem(mediaItem)
        expect(singleResultStore.mediaItem).toEqual(mediaItem)
        expect(singleResultStore.mediaType).toEqual(type)
        expect(singleResultStore.mediaId).toEqual(mediaItem.id)
      }
    )
    it("setMediaItem(null) sets the media item to null", () => {
      singleResultStore.setMediaItem(null)
      expect(singleResultStore.mediaItem).toEqual(null)
      expect(singleResultStore.mediaType).toEqual(null)
      expect(singleResultStore.mediaId).toEqual(null)
    })

    it("setMediaById sets the media if it exists in the media store", () => {
      const mediaItem = detailData[AUDIO]
      mediaStore.results.audio.items = { [mediaItem.id]: mediaItem }
      singleResultStore.setMediaById(AUDIO, mediaItem.id)

      expect(singleResultStore.mediaItem).toEqual(mediaItem)
      expect(singleResultStore.mediaType).toEqual(AUDIO)
      expect(singleResultStore.mediaId).toEqual(mediaItem.id)
    })

    it("setMediaById sets the media id and type if it doesn't exist media store", () => {
      const mediaItem = detailData[AUDIO]
      singleResultStore.setMediaById(AUDIO, mediaItem.id)

      expect(singleResultStore.mediaItem).toEqual(null)
      expect(singleResultStore.mediaType).toEqual(AUDIO)
      expect(singleResultStore.mediaId).toEqual(mediaItem.id)
    })

    it.each(supportedMediaTypes)(
      "fetchMediaItem (%s) fetches a new media if none is found in the store",
      async (type) => {
        await singleResultStore.fetchMediaItem(type, "foo")
        expect(singleResultStore.mediaItem).toEqual(detailData[type])
      }
    )
    it.each(supportedMediaTypes)(
      "fetchMediaItem (%s) re-uses existing media from the store",
      async (type) => {
        mediaStore.results[type].items = {
          [`${type}1`]: detailData[type],
        }
        await singleResultStore.fetchMediaItem(type, `${type}1`)
        expect(singleResultStore.mediaItem).toEqual(detailData[type])
      }
    )

    it.each(supportedMediaTypes)(
      "fetchMediaItem throws not found error on request error",
      async (type) => {
        const errorMessage = "error"

        mocks[type].mockImplementationOnce(() =>
          Promise.reject(new Error(errorMessage))
        )
        const expectedError = {
          message: "error",
          code: "ERR_UNKNOWN",
          details: { id: "foo" },
          requestKind: "single-result",
          searchType: type,
        }

        await singleResultStore.fetchMediaItem(type, "foo")

        expect(singleResultStore.fetchState.fetchingError).toEqual(
          expectedError
        )
      }
    )

    it.each(supportedMediaTypes)(
      "fetchMediaItem on 404 sets fetchingError and throws a new error",
      async (type) => {
        const errorResponse = new AxiosError(
          "Request failed with status code 404",
          AxiosError.ERR_BAD_REQUEST,
          {},
          {},
          {
            data: {},
            status: 404,
            statusText: "Not found",
            headers: {},
            config: {},
          }
        )

        mocks[type].mockImplementationOnce(() => Promise.reject(errorResponse))
        const id = "foo"

        const expectedError = {
          message: "Request failed with status code 404",
          statusCode: errorResponse.response.status,
          code: errorResponse.code,
          requestKind: "single-result",
          searchType: type,
          details: { id },
        }
        expect(await singleResultStore.fetch(type, id)).toEqual(null)
        expect(singleResultStore.fetchState.fetchingError).toEqual(
          expectedError
        )
      }
    )

    it("`fetch` returns current item if it matches", async () => {
      const mediaItem = detailData[AUDIO]
      singleResultStore.$patch({
        mediaItem: mediaItem,
        mediaType: AUDIO,
        mediaId: mediaItem.id,
      })
      expect(await singleResultStore.fetch(AUDIO, mediaItem.id)).toEqual(
        mediaItem
      )
      expect(mockGetMediaDetailAudio).not.toHaveBeenCalled()
    })

    it("`fetch` gets an item from a media store and fetches related media", async () => {
      const mediaType = /** @type {SupportedMediaType} */ (IMAGE)
      const expectedMediaItem = detailData[mediaType]

      mediaStore.results[IMAGE].items = { image1: expectedMediaItem }
      const actual = await singleResultStore.fetch(IMAGE, expectedMediaItem.id)

      expect(actual).toEqual(expectedMediaItem)
      expect(mockGetMediaDetailImage).not.toHaveBeenCalled()
    })
  })
})
