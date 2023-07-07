import { createPinia, setActivePinia } from "~~/test/unit/test-utils/pinia"

import { AUDIO, IMAGE, supportedMediaTypes } from "~/constants/media"
import { useMediaStore } from "~/stores/media"
import { useSingleResultStore } from "~/stores/media/single-result"
import { warn } from "~/utils/console"

const detailData = {
  [AUDIO]: { title: "audioDetails", id: "audio1", frontendMediaType: AUDIO },
  [IMAGE]: { title: "imageDetails", id: "image1", frontendMediaType: IMAGE },
}
jest.mock("axios", () => ({
  ...jest.requireActual("axios"),
  isAxiosError: jest.fn((obj) => "response" in obj),
}))

jest.mock("~/utils/console", () => ({
  warn: jest.fn(),
}))

const mockImplementation = (mediaType) => () =>
  Promise.resolve(detailData[mediaType])
const mockGetMediaDetailAudio = jest
  .fn()
  .mockImplementation(mockImplementation(AUDIO))
const mockGetMediaDetailImage = jest
  .fn()
  .mockImplementation(mockImplementation(IMAGE))
const mocks = {
  audio: mockGetMediaDetailAudio,
  image: mockGetMediaDetailImage,
}
jest.mock("~/stores/media/services", () => ({
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
  describe("state", () => {
    it("sets default state", () => {
      setActivePinia(createPinia())
      const singleResultStore = useSingleResultStore()
      expect(singleResultStore.fetchState).toEqual({
        hasStarted: false,
        isFetching: false,
        fetchingError: null,
      })
      expect(singleResultStore.audio).toEqual(null)
      expect(singleResultStore.image).toEqual(null)
      expect(singleResultStore.mediaType).toEqual(null)
    })
  })

  describe("actions", () => {
    beforeEach(() => {
      setActivePinia(createPinia())
      useMediaStore()
    })
    afterEach(() => {
      mockGetMediaDetailAudio.mockClear()
      mockGetMediaDetailImage.mockClear()
    })

    it.each(supportedMediaTypes)(
      "fetchMediaItem (%s) fetches a new media if none is found in the store",
      async (type) => {
        const singleResultStore = useSingleResultStore()

        await singleResultStore.fetchMediaItem(type, "foo")
        expect(singleResultStore[type]).toEqual(detailData[type])
      }
    )
    it.each(supportedMediaTypes)(
      "fetchMediaItem (%s) re-uses existing media from the store",
      async (type) => {
        const singleResultStore = useSingleResultStore()
        const mediaStore = useMediaStore()
        mediaStore.results[type].items = {
          [`${type}1`]: detailData[type],
        }
        await singleResultStore.fetchMediaItem(type, `${type}1`)
        expect(singleResultStore[type]).toEqual(detailData[type])
      }
    )

    it.each(supportedMediaTypes)(
      "fetchMediaItem throws not found error on request error",
      async (type) => {
        const expectedErrorMessage = "error"

        mocks[type].mockImplementationOnce(() =>
          Promise.reject(new Error(expectedErrorMessage))
        )

        const singleResultStore = useSingleResultStore()

        await expect(() =>
          singleResultStore.fetchMediaItem(type, "foo")
        ).rejects.toThrow(expectedErrorMessage)
      }
    )

    it.each(supportedMediaTypes)(
      "fetchMediaItem on 404 sets fetchingError and throws a new error",
      async (type) => {
        mocks[type].mockImplementationOnce(() =>
          Promise.reject({ response: { status: 404 } })
        )
        const expectedError = new Error(
          "Could not fetch related image for id foo"
        )

        const singleResultStore = useSingleResultStore()
        const id = "foo"

        await singleResultStore.fetch(type, id)
        expect(warn.mock.calls[0][0]).toEqual("Could not load related media: ")
        expect(warn.mock.calls[0][1]).toEqual(expectedError)

        expect(warn).toHaveBeenCalledWith(
          "Could not load related media: ",
          expectedError
        )
      }
    )
  })
})
