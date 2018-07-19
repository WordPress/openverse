
import ApiService from './ApiService';

const SocialService = {
  /**
   * Implements an endpoint to convert a provider token to an access token.
   */
  convertToken() {
    return ApiService.post('/social/token/');
  },
  /**
   * Implements an endpoint to provide access tokens.
   */
  createToken() {
    return ApiService.post('/social/convert-token/');
  },
  /**
   * Implements an endpoint to an invalidate any live sessions.
   */
  invalidateSessions() {
    return ApiService.post('/social/invalidate-sessions/');
  },
  /**
   * Implements an endpoint to revoke access or refresh tokens.
   */
  revokeToken() {
    return ApiService.post('/social/revoke-token/');
  },
};

export default SocialService;
