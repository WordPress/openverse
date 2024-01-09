// @vitest-environment jsdom
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
vi.mock("axios", async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    isAxiosError: vi.fn((obj) => "response" in obj),
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
  })
})
