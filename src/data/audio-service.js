import ApiService from './api-service'
import config from '../../nuxt.config.js'
import sampleAudioResponses from './sampleAudioResponses.json'

// TODO: Remove sample responses when Audio API is available
const AudioService = {
  /**
   * Search for audios by keyword.
   */
  search(params) {
    return config.dev
      ? Promise.resolve(sampleAudioResponses.search)
      : ApiService.query('audios', params)
  },

  getProviderCollection(params) {
    return ApiService.query('audios', params)
  },

  /**
   * Retrieve audio details by Id number.
   * SSR-called
   */
  getAudioDetail(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] AudioService.getAudioDetail() id parameter required to retrieve audio details.'
      )
    }

    return config.dev
      ? Promise.resolve(sampleAudioResponses.detail)
      : ApiService.get('audios', params.id)
  },

  getRelatedMedia(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] AudioService.getRelatedAudios() id parameter required to retrieve related audios.'
      )
    }
    return config.dev
      ? Promise.resolve(sampleAudioResponses.related)
      : ApiService.get('recommendations/audios', params.id)
  },
}

export default AudioService
