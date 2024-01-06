import { useRuntimeConfig } from "#imports"

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios"

import { warn } from "~/utils/console"
import { AUDIO, IMAGE } from "~/constants/media"

const DEFAULT_REQUEST_TIMEOUT = 30000

/**
 * Openverse Axios request config with adjusted types for our use-case.
 */
export type OpenverseAxiosRequestConfig = Required<
  Pick<AxiosRequestConfig, "headers">
> &
  AxiosRequestConfig

/**
 * Returns a slug with trailing slash for a given resource name.
 * For media types, converts the name into resource slug when necessary (i.e. pluralizes 'image'),
 * for other resources uses the resource name as the slug.
 * @param resource - the first part of the request path
 */
export const getResourceSlug = (resource: string): string => {
  const slug = { [AUDIO]: "audio", [IMAGE]: "images" }[resource] ?? resource
  return `${slug}/`
}

/**
 * @param errorCondition - if true, the `message` warning is logged in the console
 * @param message - message to display if there is an error in request
 * @param config - Axios config object that containing request url
 */
const validateRequest = (
  errorCondition: boolean,
  message: string,
  config: OpenverseAxiosRequestConfig
): void => {
  if (errorCondition) {
    warn(
      `There is a problem with the request url: ${message}.
Please check the url: ${config.baseURL}${config.url}`
    )
  }
}

/**
 * the list of options that can be passed when instantiating a new API service.
 */
export interface ApiServiceConfig {
  /** to use a different base URL than configured for the environment */
  baseUrl?: string
  /** to make authenticated requests to the API */
  accessToken?: string
  /** whether to use the `'v1/'` prefix after the base URL */
  isVersioned?: boolean
}

/**
 * the schema of the API service
 */
export interface ApiService {
  client: AxiosInstance
  query<T = unknown>(
    resource: string,
    slug: string,
    params: Record<string, string>
  ): Promise<AxiosResponse<T>>
  get<T = unknown>(
    resource: string,
    slug: string,
    params?: Record<string, string>
  ): Promise<AxiosResponse<T>>
  post<T = unknown>(
    resource: string,
    data: Parameters<AxiosInstance["post"]>[1],
    headers?: OpenverseAxiosRequestConfig["headers"]
  ): Promise<AxiosResponse<T>>
  update<T = unknown>(
    resource: string,
    slug: string,
    data: Parameters<AxiosInstance["put"]>[1],
    headers: OpenverseAxiosRequestConfig["headers"]
  ): Promise<AxiosResponse<T>>
  put<T = unknown>(
    resource: string,
    params: OpenverseAxiosRequestConfig
  ): Promise<AxiosResponse<T>>
  delete<T = unknown>(
    resource: string,
    slug: string,
    headers: OpenverseAxiosRequestConfig["headers"]
  ): Promise<AxiosResponse<T>>
}

export const createApiService = ({
  accessToken = undefined,
  isVersioned = true,
}: ApiServiceConfig = {}): ApiService => {
  const {
    public: { apiUrl: baseUrl },
  } = useRuntimeConfig()
  const axiosParams: OpenverseAxiosRequestConfig = {
    baseURL: isVersioned ? `${baseUrl}v1/` : baseUrl,
    timeout: DEFAULT_REQUEST_TIMEOUT,
    headers: {
      "User-Agent":
        "Openverse/0.1 (https://openverse.org; openverse@wordpress.org)",
      "Content-Type": "application/json",
    },
  }

  if (accessToken) {
    axiosParams.headers["Authorization"] = `Bearer ${accessToken}`
  }

  const client = axios.create(axiosParams)
  client.interceptors.request.use(function (config) {
    validateRequest(
      !config.url?.endsWith("/"),
      "API request urls should have a trailing slash",
      config as OpenverseAxiosRequestConfig
    )
    validateRequest(
      config.url?.includes("//") ?? false,
      "API request urls should not have two slashes",
      config as OpenverseAxiosRequestConfig
    )
    return config
  })
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.code === "ECONNABORTED") {
        error.message = `timeout of ${
          DEFAULT_REQUEST_TIMEOUT / 1000
        } seconds exceeded`
      }
      return Promise.reject(error)
    }
  )

  return {
    client,

    /**
     * @param resource - The endpoint of the resource
     * @param slug - the optional additional endpoint, used for collections.
     * @param params - Url parameter object
     * @returns response  The API response object
     */
    query<T = unknown>(
      resource: string,
      slug: string = "",
      params: Record<string, string> = {}
    ): Promise<AxiosResponse<T>> {
      return client.get(`${getResourceSlug(resource)}${slug}`, { params })
    },

    /**
     * @param resource - The endpoint of the resource
     * @param slug - The sub-endpoint of the resource
     * @param params - Url query parameter object
     * @returns Response The API response object
     */
    get<T = unknown>(
      resource: string,
      slug: string,
      params: Record<string, string> = {}
    ): Promise<AxiosResponse<T>> {
      return client.get(`${getResourceSlug(resource)}${slug}/`, { params })
    },

    /**
     * @param resource - The endpoint of the resource
     * @param data - Url parameter object
     * @returns Response The API response object
     */
    post<T = unknown>(
      resource: string,
      data: Parameters<(typeof client)["post"]>[1]
    ): Promise<AxiosResponse<T>> {
      return client.post(getResourceSlug(resource), data)
    },

    /**
     * @param resource - The endpoint of the resource
     * @param slug - The sub-endpoint of the resource
     * @param data - Url parameter object
     * @param headers - Headers object
     * @returns Response The API response object
     */
    update<T = unknown>(
      resource: string,
      slug: string,
      data: Parameters<(typeof client)["put"]>[1],
      headers: OpenverseAxiosRequestConfig["headers"]
    ): Promise<AxiosResponse<T>> {
      return client.put(`${getResourceSlug(resource)}${slug}`, data, {
        headers,
      })
    },

    /**
     * @param resource - The endpoint of the resource
     * @param params - Url parameter object
     * @returns Response The API response object
     */
    put<T = unknown>(
      resource: string,
      params: OpenverseAxiosRequestConfig
    ): Promise<AxiosResponse<T>> {
      return client.put(getResourceSlug(resource), params)
    },

    /**
     * @param resource - The endpoint of the resource
     * @param slug - The sub-endpoint of the resource
     * @param headers - Headers object
     * @returns Response The API response object
     */
    delete<T = unknown>(
      resource: string,
      slug: string,
      headers: OpenverseAxiosRequestConfig["headers"]
    ): Promise<AxiosResponse<T>> {
      return client.delete(`${getResourceSlug(resource)}${slug}`, { headers })
    },
  }
}
