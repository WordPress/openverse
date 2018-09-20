
import ApiService from './ApiService';

const LinkService = {
  /**
   * Implements an endpoint to create a link.
   */
  createLink(params) {
    return ApiService.post('/link', { full_url: params.url });
  },
  /**
   * Implements an endpoint to get a shortened URL.
  */
  resolveLInk(params) {
    return ApiService.get('/link', { path: params.path });
  },
};

export default LinkService;
