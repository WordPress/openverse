import { createPinia, setActivePinia } from 'pinia'

import { initialFetchState } from '~/composables/use-fetch-state'
import { AUDIO, IMAGE, supportedMediaTypes } from '~/constants/media'
import { useMediaStore } from '~/stores/media'
import { useSingleResultStore } from '~/stores/media/single-result'
import { services } from '~/stores/media/services'

const detailData = {
  [AUDIO]: { title: 'audioDetails', id: 'audio1', frontendMediaType: AUDIO },
  [IMAGE]: { title: 'imageDetails', id: 'image1', frontendMediaType: IMAGE },
}
jest.mock('axios', () => ({
  ...jest.requireActual('axios'),
  isAxiosError: jest.fn((obj) => 'response' in obj),
}))
jest.mock('~/stores/media/services', () => ({
  services: {
    audio: /** @type {import('~/data/services').MediaService} */ ({
      getMediaDetail: jest.fn(),
    }),
    image: /** @type {import('~/data/services').MediaService} */ ({
      getMediaDetail: jest.fn(),
    }),
  },
}))
for (const mediaType of [AUDIO, IMAGE]) {
  services[mediaType].getMediaDetail.mockImplementation(() =>
    Promise.resolve(detailData[mediaType])
  )
}
describe('Media Item Store', () => {
  describe('state', () => {
    it('sets default state', () => {
      setActivePinia(createPinia())
      const singleResultStore = useSingleResultStore()
      expect(singleResultStore.fetchState).toEqual(initialFetchState)
      expect(singleResultStore.mediaItem).toEqual(null)
      expect(singleResultStore.mediaType).toEqual(null)
    })
  })

  describe('actions', () => {
    beforeEach(() => {
      setActivePinia(createPinia())
      useMediaStore()
    })

    it.each(supportedMediaTypes)(
      'fetchMediaItem (%s) fetches a new media if none is found in the store',
      async (type) => {
        const singleResultStore = useSingleResultStore()

        await singleResultStore.fetchMediaItem(type, 'foo')
        expect(singleResultStore.mediaItem).toEqual(detailData[type])
      }
    )
    it.each(supportedMediaTypes)(
      'fetchMediaItem (%s) re-uses existing media from the store',
      async (type) => {
        const singleResultStore = useSingleResultStore()
        const mediaStore = useMediaStore()
        mediaStore.results[type].items = {
          [`${type}1`]: detailData[type],
        }
        await singleResultStore.fetchMediaItem(type, `${type}1`)
        expect(singleResultStore.mediaItem).toEqual(detailData[type])
      }
    )

    it.each(supportedMediaTypes)(
      'fetchMediaItem throws not found error on request error',
      async (type) => {
        const expectedErrorMessage = 'error'

        services[type].getMediaDetail.mockImplementationOnce(() =>
          Promise.reject(new Error(expectedErrorMessage))
        )

        const singleResultStore = useSingleResultStore()

        await expect(() =>
          singleResultStore.fetchMediaItem(type, 'foo')
        ).rejects.toThrow(expectedErrorMessage)
      }
    )

    it.each(supportedMediaTypes)(
      'fetchMediaItem on 404 sets fetchingError and throws a new error',
      async (type) => {
        services[type].getMediaDetail.mockImplementationOnce(() =>
          Promise.reject({ response: { status: 404 } })
        )
        const singleResultStore = useSingleResultStore()
        const id = 'foo'
        await expect(() =>
          singleResultStore.fetchMediaItem(type, id)
        ).rejects.toThrow(`Media of type ${type} with id ${id} not found`)
      }
    )
  })
})
