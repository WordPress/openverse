import { VersionedApiService } from './api-service'

/**
 * Service that calls API to get Media Provider stats
 * @param {('image'|'audio')} mediaType
 * @constructor
 */
const MediaProviderService = (mediaType) => ({
  /**
   * Implements an endpoint to get audio provider statistics.
   * SSR-called
   */
  async getProviderStats() {
    try {
      return await VersionedApiService.get(mediaType, 'stats')
    } catch (error) {
      console.error(`Error fetching ${mediaType} providers`, error)
    }
  },
})

export default MediaProviderService
