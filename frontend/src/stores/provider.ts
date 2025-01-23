import { useNuxtApp } from "#imports"

import { defineStore } from "pinia"

import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  type SupportedMediaType,
  supportedMediaTypes,
} from "#shared/constants/media"
import { capitalCase } from "#shared/utils/case"
import type { MediaProvider } from "#shared/types/media-provider"
import type { FetchingError, FetchState } from "#shared/types/fetch-state"

export interface ProviderState {
  providers: {
    audio: MediaProvider[]
    image: MediaProvider[]
  }
  fetchState: FetchState
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
    fetchState: { status: "idle", error: null },
    sourceNames: {
      [AUDIO]: [],
      [IMAGE]: [],
    },
  }),

  actions: {
    _endFetching(error?: FetchingError) {
      if (error) {
        this.fetchState = { status: "error", error }
      } else {
        this.fetchState = { status: "success", error: null }
      }
    },
    _startFetching() {
      this.fetchState = { status: "fetching", error: null }
    },

    _updateFetchState(action: "start" | "end", option?: FetchingError) {
      if (action === "start") {
        this._startFetching()
      } else {
        this._endFetching(option)
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

    setMediaTypeProviders(
      mediaType: SupportedMediaType,
      providers: MediaProvider[]
    ) {
      if (!Array.isArray(providers) || !providers.length) {
        return
      }
      this.providers[mediaType] = sortProviders(providers)
      this.sourceNames[mediaType] = providers.map((p) => p.source_name)
    },

    async fetchProviders() {
      this._updateFetchState("start")
      const { $processFetchingError } = useNuxtApp()
      try {
        const res =
          await $fetch<Record<SupportedMediaType, MediaProvider[]>>(
            `/api/sources/`
          )
        if (!res) {
          throw new Error("No sources data returned from the API")
        }
        for (const mediaType of supportedMediaTypes) {
          this.setMediaTypeProviders(mediaType, res[mediaType])
        }
        this._updateFetchState("end")
      } catch (error: unknown) {
        const errorData = $processFetchingError(error, ALL_MEDIA, "provider")
        this._updateFetchState("end", errorData)
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
