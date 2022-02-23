import ApiService from '~/data/api-service'

import decodeMediaData from '~/utils/decode-media-data'

/**
 * @template {import('../store/types').FrontendMediaType} [T=any]
 */
class MediaService {
  /**
   * @param {T} mediaType
   */
  constructor(mediaType) {
    /** @type {T} */
    this.mediaType = mediaType
  }

  /**
   * Decodes the text data to avoid encoding problems.
   * Also, converts the results from an array of media objects into an object with
   * media id as keys.
   * @param {import('axios').AxiosResponse<T>} data
   * @returns {import('../store/types').MediaStoreResult<T>}
   */
  transformResults(data) {
    return {
      ...data,
      results: data.results.reduce((acc, item) => {
        acc[item.id] = decodeMediaData(item, this.mediaType)
        return acc
      }, /** @type {Record<string, import('../store/types').DetailFromMediaType<T>>} */ ({})),
    }
  }

  /**
   * Search for media items by keyword.
   * @param {import('../store/types').ApiQueryParams} params
   * @return {Promise<import('axios').AxiosResponse<import('../store/types').MediaResult<T[]>>>}
   */
  async search(params) {
    const res = await ApiService.query(this.mediaType, params)
    return this.transformResults(res.data)
  }

  /**
   * Retrieve media details by its id.
   * SSR-called
   * @param {{ id: string }} params
   * @return {Promise<import('axios').AxiosResponse<import('../store/types').MediaResult<T>>>}
   */
  async getMediaDetail(params) {
    if (!params.id) {
      throw new Error(
        `MediaService.getMediaDetail() id parameter required to retrieve ${this.mediaType} details.`
      )
    }

    const res = await ApiService.get(this.mediaType, params.id)
    return decodeMediaData(res.data, this.mediaType)
  }

  /**
   * Retrieve related media
   * @param {{ id: string }} params
   * @return {Promise<import('axios').AxiosResponse<import('../store/types').MediaResult<T[]>>>}
   */
  async getRelatedMedia(params) {
    if (!params.id) {
      throw new Error(
        `MediaService.getRelatedMedia() id parameter required to retrieve related media.`
      )
    }

    const res = await ApiService.get(this.mediaType, `${params.id}/related`)
    return {
      ...res.data,
      results: res.data.results.map((item) =>
        decodeMediaData(item, this.mediaType)
      ),
    }
  }
}

export default MediaService
