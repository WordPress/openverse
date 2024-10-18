import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import { capitalCase } from "~/utils/case"
import {
  AUDIO,
  IMAGE,
  type SupportedMediaType,
  supportedMediaTypes,
} from "~/constants/media"

import type { MediaProvider } from "~/types/media-provider"
import type { FetchingError, FetchState } from "~/types/fetch-state"

import { useApiClient } from "~/composables/use-api-client"

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
export const sortProviders = (data: MediaProvider[]): MediaProvider[] => {
  if (!data.length || !Array.isArray(data)) {
    return []
  }
  return data.sort((sourceObjectA, sourceObjectB) => {
    const nameA = sourceObjectA.source_name.toUpperCase()
    const nameB = sourceObjectB.source_name.toUpperCase()
    return nameA.localeCompare(nameB)
  })
}

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
      if (action === "start") {
        this._startFetching(mediaType)
      } else {
        this._endFetching(mediaType, option)
      }
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
      return (
        this._getProvider(providerCode, mediaType)?.display_name ||
        capitalCase(providerCode)
      )
    },

    /**
     * Returns the source URL given the source code and media type.
     */
    getSourceUrl(providerCode: string, mediaType: SupportedMediaType) {
      return this._getProvider(providerCode, mediaType)?.source_url
    },

    async fetchProviders() {
      await Promise.allSettled(
        supportedMediaTypes.map((mediaType) =>
          this.fetchMediaTypeProviders(mediaType)
        )
      )
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

      const client = useApiClient()

      try {
        const res = await client.stats(mediaType)
        sortedProviders = sortProviders(res ?? [])
        this._updateFetchState(mediaType, "end")
      } catch (error: unknown) {
        const { $processFetchingError } = useNuxtApp()
        const errorData = $processFetchingError(error, mediaType, "provider")

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
})
