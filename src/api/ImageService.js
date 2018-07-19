
import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import { API_URL } from '@/config/prod-env'
import ApiService from './ApiService'

export const ImageService = {
  /**
   * Search for images by keyword.
   */
  search (params) {
    if (typeof params !== 'object' || params.hasOwnParamater('q')) {
      throw new Error('[RWV] ImageService.search() q parameter required to search images.')
    }
    
    return ApiService.query('image/search', params);
  }
  /**
   * Retreive image details by Id number.
   */
  getImageDetail (id) {
    if (isNaN(id)) {
      throw new Error('[RWV] ImageService.getImageDetail() id parameter required to retreive image details.')
    }
    
    return ApiService.get('image', `/image//${id}`);
  }
}
