import { defineStore } from "pinia"
import { ssrRef } from "@nuxtjs/composition-api"

import { capitalCase } from "~/utils/case"
import { env } from "~/utils/env"
import {
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedMediaTypes,
} from "~/constants/media"

import type { MediaProvider } from "~/types/media-provider"
import type { FetchingError, FetchState } from "~/types/fetch-state"

import type { Ref } from "vue"

export interface ProviderState {
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

/**
 * Sorts providers by their source_name property.
 * @param data - initial unordered list of providers
 */
const sortProviders = (data: MediaProvider[]): MediaProvider[] => {
  return [...data].sort((sourceObjectA, sourceObjectB) => {
    const nameA = sourceObjectA.source_name.toUpperCase()
    const nameB = sourceObjectB.source_name.toUpperCase()
    return nameA.localeCompare(nameB)
  })
}
/**
 * Timestamp is used to limit the update frequency to one every 60 minutes per request.
 */
const lastUpdated: Ref<Date | null> = ssrRef(null)

const updateFrequency = parseInt(env.providerUpdateFrequency, 10)

export const useProviderStore = defineStore("provider", {
  state: (): ProviderState => ({
    providers: {
      [AUDIO]: [],
      [IMAGE]: [],
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
        lastUpdated.value = new Date()
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
      try {
        const res = await this.$nuxt.$apiClient(
          `GET v1/${mediaType === "audio" ? "audio" : "images"}/stats/`
        )
        if (res.meta.status !== 200) {
          throw res
        }
        sortedProviders = sortProviders(res.body)
        this._updateFetchState(mediaType, "end")
      } catch (error: unknown) {
        console.error(error)
        const errorData = this.$nuxt.$processFetchingError(
          error,
          mediaType,
          "provider"
        )

        // Fallback on existing providers if there was an error
        sortedProviders = this.providers[mediaType]
        this._updateFetchState(mediaType, "end", errorData)
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
      if (noData || !lastUpdated.value) {
        return true
      }

      const timeSinceLastUpdate =
        new Date().getTime() - new Date(lastUpdated.value).getTime()
      return timeSinceLastUpdate > updateFrequency
    },
  },
})
