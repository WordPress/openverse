
import ApiService from './ApiService';

const ShareListService = {
  /**
   * Implements an endpoint to create a list.
   */
  createList(params) {
    return ApiService.post('/list', { title: params.listTitle, images: params.images });
  },
  /**
   * Implements an endpoint to create a shortened list url.
   */
  createShortenedListURL(params) {
    return ApiService.post('/link_create', { url: params.url });
  },
  /**
   * Implements an endpoint to edit a list.
   */
  editList(params) {
    ApiService.setHeader({ auth: params.auth });

    return ApiService.update('/list_update', params.id, params.ids);
  },
  /**
   * Implements an endpoint to delete a list.
   */
  deleteList(params) {
    ApiService.setHeader({ auth: params.auth });

    return ApiService.delete('/list_delete', params.id);
  },
  /**
   * Implements an endpoint to get a list based on ID.
  */
  getList(params) {
    return ApiService.get('/list', params.id);
  },
};

export default ShareListService;
