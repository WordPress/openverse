import ApiService from './ApiService'
import config from '../../nuxt.config.js'
import sampleAudioResponses from './sampleAudioResponses.json'

// TODO: Remove sample responses when Audio API is available
const AudioService = {
  /**
   * Search for audios by keyword.
   * @param {Object} params
   * @return {Promise<{data: Object}>}
   */
  search(params) {
    return config.dev
      ? Promise.resolve({ data: sampleAudioResponses.search })
      : ApiService.query('audios', params)
  },

  getProviderCollection(params) {
    return ApiService.query('audios', params)
  },

  /**
   * Retrieve audio details by Id number.
   * SSR-called
   * @param {{id: string}} params
   * @return {Promise<{data: Object}>}
   */
  getMediaDetail(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] AudioService.getMediaDetail() id parameter required to retrieve audio details.'
      )
    }

    return config.dev
      ? Promise.resolve({ data: sampleAudioResponses.detail })
      : ApiService.get('audios', params.id)
  },

  /**
   * Retrieve related media
   * @param params
   * @return {Promise<{data: Object}>}
   */
  getRelatedMedia(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] AudioService.getRelatedMedia() id parameter required to retrieve related audios.'
      )
    }
    return config.dev
      ? Promise.resolve({ data: sampleAudioResponses.related })
      : ApiService.get('recommendations/audios', params.id)
  },
}

export default AudioService
