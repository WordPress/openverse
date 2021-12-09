import config from '../../nuxt.config.js'
import sampleAudioResponses from './sample-audio-responses.json'

import ApiService from '~/data/api-service'
import BaseMediaService from '~/data/base-media-service'

import { AUDIO } from '~/constants/media'

// TODO: Remove sample responses when Audio API is available
const AudioService = {
  ...BaseMediaService(AUDIO),

  /**
   * Search for audios by keyword.
   * @param {Object} params
   * @return {Promise<{data: any}>}
   */
  search(params) {
    if (config.dev) {
      const data = JSON.parse(JSON.stringify(sampleAudioResponses.search))
      return Promise.resolve({ data })
    }
    return ApiService.query('audios', params)
  },

  getProviderCollection(params) {
    return ApiService.query('audios', params)
  },

  /**
   * Retrieve audio details by Id number.
   * SSR-called
   * @param {object} params
   * @param {string} params.id
   * @return {Promise<{data: any}>}
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
   * @param {string} params.id
   * @return {Promise<{data: any}>}
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
