import ApiService from './api-service'

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
      // Can't just use the mediaType value because it's 'image', not 'images'.
      // We should find a way to normalize this.
      if (mediaType == 'image') {
        return await ApiService.get('images', 'stats')
      }
      return await ApiService.get(mediaType, 'stats')
    } catch (error) {
      console.error(`Error fetching ${mediaType} providers`, error)
    }
  },
})

export default MediaProviderService
