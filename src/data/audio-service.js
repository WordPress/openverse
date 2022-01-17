import ApiService from '~/data/api-service'
import BaseMediaService from '~/data/base-media-service'

import { AUDIO } from '~/constants/media'

const AudioService = {
  ...BaseMediaService(AUDIO),

  /**
   * Search for audios by keyword.
   * @param {Object} params
   * @return {Promise<{data: any}>}
   */
  search(params) {
    return ApiService.query('audio/', params)
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

    return ApiService.get('audio', params.id)
  },

  /**
   * Retrieve related media
   * @param {object} params
   * @param {string} params.id
   * @return {Promise<{data: any}>}
   */
  getRelatedMedia(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] AudioService.getRelatedMedia() id parameter required to retrieve related audios.'
      )
    }

    return ApiService.get('audio', `${params.id}/related`)
  },
}

export default AudioService
