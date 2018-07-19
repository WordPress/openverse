
import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import { API_URL } from '@/config/prod-env'
import ApiService from './ApiService'

export const HealthCheckService = {
  /**
   * Retreive the status of the api.
   */
  getStatus () {
    return ApiService.get('healthcheck');
  }
}
