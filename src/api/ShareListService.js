
import ApiService from './ApiService';

const ShareListService = {
  /**
   * Implements an endpoint to create a list.
   */
  createList(params) {
    return ApiService.post('/list', { title: params.listTitle, images: params.images });
  },
  /**
   * Implements an endpoint to get a list based on ID.
  */
  getList(params) {
    return ApiService.get('/list', params.id);
  },
};

export default ShareListService;
