
import ApiService from './ApiService';

const ImageService = {
  /**
   * Search for images by keyword.
   */
  search(params) {
    return ApiService.query('image/search', params);
  },

  getProviderCollection(params) {
    return ApiService.query(`image/browse/${params.provider}`, params);
  },

  /**
   * Retreive image details by Id number.
   */
  getImageDetail(params) {
    if (!params.id) {
      throw new Error('[RWV] ImageService.getImageDetail() id parameter required to retreive image details.');
    }

    return ApiService.get('image', params.id);
  },

  getRelatedImages(params) {
    if (!params.id) {
      throw new Error('[RWV] ImageService.getRelatedImages() id parameter required to retreive related images.');
    }

    return ApiService.get('image/related', params.id);
  },
};

export default ImageService;
