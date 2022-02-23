import axios from 'axios'
import { warn } from '~/utils/warn'
import { AUDIO, IMAGE } from '~/constants/media'

const DEFAULT_REQUEST_TIMEOUT = 30000

/**
 * Returns a slug with trailing slash for a given resource name.
 * For media types, converts the name into resource slug when necessary (i.e. pluralizes 'image'),
 * for other resources uses the resource name as the slug.
 * @param {string} resource
 * @returns {string}
 */
const getResourceSlug = (resource) => {
  const slug = { [AUDIO]: 'audio', [IMAGE]: 'images' }[resource] ?? resource
  return `${slug}/`
}
/**
 * @param {boolean} errorCondition
 * @param {string} message
 * @param {import('axios').AxiosRequestConfig} config
 */
const validateRequest = (errorCondition, message, config) => {
  if (errorCondition) {
    warn(
      `There is a problem with the request url: ${message}.
Please check the url: ${config.baseURL}${config.url}`
    )
  }
}

/**
 *
 * @param {string} [baseUrl]
 */
export const createApiService = (baseUrl = process.env.apiUrl) => {
  const client = axios.create({
    baseURL: baseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
  })
  client.interceptors.request.use(function (config) {
    validateRequest(
      !config.url?.endsWith('/'),
      'API request urls should have a trailing slash',
      config
    )
    validateRequest(
      config.url?.includes('//') ?? false,
      'API request urls should not have two slashes',
      config
    )
    return config
  })
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === 'ECONNABORTED') {
        return Promise.reject({
          message: `timeout of ${
            DEFAULT_REQUEST_TIMEOUT / 1000
          } seconds exceeded`,
          ...error,
        })
      }
      return Promise.reject(error)
    }
  )

  return {
    /**
     * @template [T=unknown]
     * @param {string} resource  The endpoint of the resource
     * @param {import('axios').AxiosRequestConfig['params']} params  Url parameter object
     * @returns {Promise<import('axios').AxiosResponse<T>>} response  The API response object
     */
    query(resource, params) {
      return client.get(`${getResourceSlug(resource)}`, { params })
    },

    /**
     * @template [T=unknown]
     * @param {string} resource  The endpoint of the resource
     * @param {string} slug The sub-endpoint of the resource
     * @returns {Promise<import('axios').AxiosResponse<T>>} Response The API response object
     */
    get(resource, slug) {
      return client.get(`${getResourceSlug(resource)}${slug}/`)
    },

    /**
     * @template [T=unknown]
     * @param {string} resource  The endpoint of the resource
     * @param {Parameters<typeof client['post']>[1]} data Url parameter object
     * @returns {Promise<import('axios').AxiosResponse<T>>} Response The API response object
     */
    post(resource, data) {
      return client.post(getResourceSlug(resource), data)
    },

    /**
     * @template [T=unknown]
     * @param {string} resource  The endpoint of the resource
     * @param {string} slug The sub-endpoint of the resource
     * @param {Parameters<typeof client['put']>[1]} data Url parameter object
     * @param {import('axios').AxiosRequestConfig['headers']} headers Headers object
     * @returns {Promise<import('axios').AxiosResponse<T>>} Response The API response object
     */
    update(resource, slug, data, headers) {
      return client.put(`${getResourceSlug(resource)}${slug}`, data, {
        headers,
      })
    },

    /**
     * @param {string} resource  The endpoint of the resource
     * @param {import('axios').AxiosRequestConfig} params Url parameter object
     * @returns {Promise<import('axios').AxiosResponse<any>>} Response The API response object
     */
    put(resource, params) {
      return client.put(getResourceSlug(resource), params)
    },

    /**
     * @param {string} resource  The endpoint of the resource
     * @param {string} slug The sub-endpoint of the resource
     * @param {import('axios').AxiosRequestConfig['headers']} headers Headers object
     * @returns {Promise<import('axios').AxiosResponse<any>>} Response The API response object
     */
    delete(resource, slug, headers) {
      return client.delete(`${getResourceSlug(resource)}${slug}`, { headers })
    },
  }
}

const ApiService = createApiService()
export default ApiService
