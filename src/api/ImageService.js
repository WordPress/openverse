
import ApiService from './ApiService';

const ImageService = {
  /**
   * Search for images by keyword.
   */
  search(params) {
    if (typeof params !== 'object' ||
      Object.prototype.hasOwnProperty.call(params, 'q') === false) {
      throw new Error('[RWV] ImageService.search() q parameter required to search images.');
    }

    Object.assign(params, params.filters);

    return ApiService.query('image/search', params);
  },
  /**
   * Retreive image details by Id number.
   */
  getImageDetail(params) {
    if (params.id && isNaN(params.id)) {
      throw new Error('[RWV] ImageService.getImageDetail() id parameter required to retreive image details.');
    }

    return ApiService.get('image', params.id);
  },
};

export default ImageService;
