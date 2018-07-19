
import ApiService from './ApiService';

const HealthCheckService = {
  /**
   * Retreive the status of the api.
   */
  getStatus() {
    return ApiService.get('healthcheck');
  },
};

export default HealthCheckService;
