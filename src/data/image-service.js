import ApiService from './api-service'
import BaseMediaService from '~/data/base-media-service.js'

import { IMAGE } from '~/constants/media'

const ImageService = {
  ...BaseMediaService(IMAGE),

  /**
   * Search for images by keyword.
   */
  search(params) {
    return ApiService.query('images', params)
  },

  getProviderCollection(params) {
    return ApiService.query('images', params)
  },

  /**
   * Retrieve image details by Id number.
   * SSR-called
   */
  getMediaDetail(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] ImageService.getMediaDetail() id parameter required to retrieve image details.'
      )
    }

    return ApiService.get('images', params.id)
  },

  getRelatedMedia(params) {
    if (!params.id) {
      throw new Error(
        '[RWV] ImageService.getRelatedImages() id parameter required to retrieve related images.'
      )
    }

    return ApiService.get('recommendations/images', params.id)
  },
}

export default ImageService
