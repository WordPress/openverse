import { useNuxtApp, useRuntimeConfig, useRequestEvent } from "#imports"

import { defineStore } from "pinia"

import axios from "axios"

import { capitalCase } from "~/utils/case"
import { parseFetchingError } from "~/utils/errors"
import {
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedMediaTypes,
} from "~/constants/media"

import type { MediaProvider } from "~/types/media-provider"
import type { FetchingError, FetchState } from "~/types/fetch-state"
import { DEFAULT_REQUEST_TIMEOUT } from "~/utils/query-utils"

import { sortProviders } from "~/utils/provider"

import { providers } from "#nuxt-prepare"

export interface ProviderState {
  /**
   * Timestamp is used to limit the update frequency to one every 60 minutes per request.
   */
  lastUpdated: null | Date
  providers: {
    audio: MediaProvider[]
    image: MediaProvider[]
  }
  fetchState: {
    audio: FetchState
    image: FetchState
  }
  sourceNames: {
    audio: string[]
    image: string[]
  }
}

export const useProviderStore = defineStore("provider", {
  state: (): ProviderState => ({
    lastUpdated: null,
    providers: {
      [AUDIO]: providers?.audio ?? [],
      [IMAGE]: providers?.image ?? [],
    },
    fetchState: {
      [AUDIO]: { isFetching: false, hasStarted: false, fetchingError: null },
      [IMAGE]: { isFetching: false, hasStarted: false, fetchingError: null },
    },
    sourceNames: {
      [AUDIO]: [],
      [IMAGE]: [],
    },
  }),

  actions: {
    _endFetching(mediaType: SupportedMediaType, error?: FetchingError) {
      this.fetchState[mediaType].fetchingError = error || null
      if (error) {
        this.fetchState[mediaType].isFinished = true
        this.fetchState[mediaType].hasStarted = true
      } else {
        this.fetchState[mediaType].hasStarted = true
      }
      this.fetchState[mediaType].isFetching = false
    },
    _startFetching(mediaType: SupportedMediaType) {
      this.fetchState[mediaType].isFetching = true
      this.fetchState[mediaType].hasStarted = true
    },

    _updateFetchState(
      mediaType: SupportedMediaType,
      action: "start" | "end",
      option?: FetchingError
    ) {
      action === "start"
        ? this._startFetching(mediaType)
        : this._endFetching(mediaType, option)
    },
    async getProviders() {
      await this.fetchMediaProviders()
      return this.providers
    },

    _getProvider(providerCode: string, mediaType: SupportedMediaType) {
      return this.providers[mediaType].find(
        (p) => p.source_name === providerCode
      )
    },

    /**
     * Returns the display name for provider if available, or capitalizes the given providerCode.
     *
     * @param providerCode - the `source_name` property of the provider
     * @param mediaType - mediaType of the provider
     */
    getProviderName(providerCode: string, mediaType: SupportedMediaType) {
      const provider = this._getProvider(providerCode, mediaType)
      return provider?.display_name || capitalCase(providerCode)
    },

    /**
     * Returns the source URL given the source code and media type.
     */
    getSourceUrl(providerCode: string, mediaType: SupportedMediaType) {
      const provider = this._getProvider(providerCode, mediaType)
      return provider?.source_url
    },

    /**
     * Fetches provider data if no data is available, or if the data is too old.
     * On successful fetch updates lastUpdated value.
     */
    async fetchMediaProviders() {
      if (this.needsUpdate) {
        await Promise.allSettled(
          supportedMediaTypes.map((mediaType) =>
            this.fetchMediaTypeProviders(mediaType)
          )
        )
        this.lastUpdated = new Date()
      }
    },

    /**
     * Fetches provider stats for a set media type.
     * Does not update provider stats if there's an error.
     */
    async fetchMediaTypeProviders(
      mediaType: SupportedMediaType
    ): Promise<void> {
      this._updateFetchState(mediaType, "start")
      let sortedProviders = [] as MediaProvider[]
      const { $sentry } = useNuxtApp()

      const nitroOrigin = useRequestEvent()?.context.siteConfigNitroOrigin

      // TODO: Check if baseURL works in prod.
      let baseURL = nitroOrigin ? nitroOrigin : location?.origin
      baseURL = baseURL.replace("localhost", "0.0.0.0")
      try {
        const res: MediaProvider[] = await axios.get(
          `/api/${mediaType === "image" ? "images" : "audio"}/stats/`,
          {
            baseURL,
            timeout: DEFAULT_REQUEST_TIMEOUT,
          }
        )
        sortedProviders = sortProviders(res)
        this._updateFetchState(mediaType, "end")
      } catch (error: unknown) {
        const errorData = parseFetchingError(error, mediaType, "provider")

        // Fallback on existing providers if there was an error
        sortedProviders = this.providers[mediaType]
        this._updateFetchState(mediaType, "end", errorData)
        $sentry.captureException(error, { extra: { errorData } })
      } finally {
        this.providers[mediaType] = sortedProviders
        this.sourceNames[mediaType] = sortedProviders.map((p) => p.source_name)
      }
    },

    /**
     * Returns true if the given source name exists in the given media type sources list.
     */
    isSourceNameValid(
      mediaType: SupportedMediaType,
      sourceName: string
    ): boolean {
      return this.sourceNames[mediaType].includes(sourceName)
    },
  },

  getters: {
    /**
     * Fetch providers only if there is no data, or if the last update for current request
     * was more than 1 hour ago.
     */
    needsUpdate(state) {
      const noData = supportedMediaTypes.some(
        (mediaType) => !state.providers[mediaType].length
      )
      if (noData || !state.lastUpdated) {
        return true
      }
      const {
        public: { providerUpdateFrequency },
      } = useRuntimeConfig()

      const timeSinceLastUpdate =
        new Date().getTime() - new Date(state.lastUpdated).getTime()
      return timeSinceLastUpdate > providerUpdateFrequency
    },
  },
})
