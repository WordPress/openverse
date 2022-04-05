import { getAdditionalSources } from '~/utils/get-additional-sources'
import { AUDIO, IMAGE, MediaType, MODEL_3D, VIDEO } from '~/constants/media'

/**
 * These tests do not test the health or uptime of URLS, only that a valid URL
 * string is returned.
 */
describe('getAdditionalSources', () => {
  it.each`
    mediaType
    ${AUDIO}
    ${VIDEO}
    ${IMAGE}
    ${MODEL_3D}
  `(
    `returns a URL for each $mediaType source`,
    ({ mediaType }: { mediaType: MediaType }) => {
      const search = { q: 'dogs' }
      const audioSources = getAdditionalSources(mediaType, search)
      const urls = audioSources.map((source) => source.url)

      expect(urls.every((url) => url?.startsWith('http'))).toBeTruthy()
    }
  )
})
