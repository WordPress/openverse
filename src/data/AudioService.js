import ApiService from './ApiService'
import config from '../../nuxt.config.js'
import sampleAudioResponses from './sampleAudioResponses.json'

/**
 * Audio Detail object
 * @typedef {Object} AudioDetail
 * @property {string} id
 * @property {string} foreign_landing_url
 * @property {string} creator
 * @property {string} creator_url
 * @property {string} url
 * @property {string} license
 * @property {string} license_version
 * @property {string} license_url
 * @property {string} provider
 * @property {string} source
 * @property {any} tags
 * @property {string} attribution
 * @property {any} audio_set
 * @property {any} genres
 * @property {any} duration
 * @property {number} [bit_rate]
 * @property {number} [sample_rate]
 * @property {any} [alt_files]
 * @property {string} detail_url
 * @property {string} related_url
 */

// TODO: Remove sample responses when Audio API is available
const AudioService = {
  /**
   * Search for audios by keyword.
   * @param params
   * @return {Promise<APIResponse<MediaResult>>}
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
   * @param params
   * @return {Promise<APIResponse<MediaResult<AudioDetail>>>}
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
   * @return {Promise<{MediaResult}>}
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
