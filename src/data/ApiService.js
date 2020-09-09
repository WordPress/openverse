import axios from 'axios'

const DEFAULT_REQUEST_TIMEOUT = 30000

export const createApiService = (baseUrl = process.env.API_URL) => {
  const client = axios.create({
    baseURL: baseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
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
    query(resource, params) {
      return client.get(resource, { params })
    },

    get(resource, slug) {
      return client.get(`${resource}/${slug}`)
    },

    post(resource, params) {
      return client.post(`${resource}`, params)
    },

    update(resource, slug, params, headers) {
      return client.put(`${resource}/${slug}`, params, { headers })
    },

    put(resource, params) {
      return client.put(`${resource}`, params)
    },

    delete(resource, slug, headers) {
      return client.delete(`${resource}/${slug}`, { headers })
    },
  }
}

const ApiService = createApiService()
export default ApiService
