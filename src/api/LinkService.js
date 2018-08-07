
import ApiService from './ApiService';

const LinkService = {
  /**
   * Implements an endpoint to create a link.
   */
  createLink(params) {
    return ApiService.post('/link', { fullURL: params.fullURL });
  },
  /**
   * Implements an endpoint to get a shortened URL.
  */
  resolveLInk(params) {
    return ApiService.get('/path', { path: params.path });
  },
};

export default LinkService;
