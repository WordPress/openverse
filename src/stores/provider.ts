import { capital } from 'case'
import { defineStore } from 'pinia'
import { Ref, ssrRef } from '@nuxtjs/composition-api'
import axios from 'axios'

import { env } from '~/utils/env'
import {
  AUDIO,
  IMAGE,
  SupportedMediaType,
  supportedMediaTypes,
} from '~/constants/media'
import { warn } from '~/utils/console'
import { providerServices } from '~/data/media-provider-service'
import type { MediaProvider } from '~/models/media-provider'
import {
  FetchState,
  initialFetchState,
  updateFetchState,
} from '~/composables/use-fetch-state'
import { useSearchStore } from '~/stores/search'

export interface ProviderState {
  providers: {
    audio: MediaProvider[]
    image: MediaProvider[]
  }
  fetchState: {
    audio: FetchState
    image: FetchState
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

export const useProviderStore = defineStore('provider', {
  state: (): ProviderState => ({
    providers: {
      [AUDIO]: [],
      [IMAGE]: [],
    },
    fetchState: {
      [AUDIO]: { ...initialFetchState },
      [IMAGE]: { ...initialFetchState },
    },
  }),

  actions: {
    _updateFetchState(
      mediaType: SupportedMediaType,
      action: 'end' | 'start',
      option?: string
    ) {
      this.fetchState[mediaType] = updateFetchState(
        this.fetchState[mediaType],
        action,
        option
      )
    },

    /**
     * Returns the display name for provider if available, or capitalizes the given providerCode.
     *
     * @param providerCode - the `source_name` property of the provider
     * @param mediaType - mediaType of the provider
     */
    getProviderName(providerCode: string, mediaType: SupportedMediaType) {
      const provider = this.providers[mediaType].find(
        (p) => p.source_name === providerCode
      )
      return provider?.display_name || capital(providerCode)
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
     * Fetches providers for a set media type, and initializes the provider filters
     * by calling the search store `initProviderFilters` method.
     */
    async fetchMediaTypeProviders(
      mediaType: SupportedMediaType
    ): Promise<void> {
      this._updateFetchState(mediaType, 'start')
      let sortedProviders = [] as MediaProvider[]
      try {
        const res = await providerServices[mediaType].getProviderStats()
        sortedProviders = sortProviders(res.data)
        const searchStore = useSearchStore()
        searchStore.initProviderFilters({
          mediaType,
          providers: sortedProviders,
        })
        this._updateFetchState(mediaType, 'end')
      } catch (error: unknown) {
        let errorMessage = `There was an error fetching media providers for ${mediaType}`
        if (error instanceof Error) {
          errorMessage =
            axios.isAxiosError(error) && 'response' in error
              ? `${errorMessage}: ${error.code}`
              : `${errorMessage}: ${error?.message}`
        }
        warn(errorMessage)
        this._updateFetchState(mediaType, 'end', errorMessage)
      } finally {
        this.providers[mediaType] = sortedProviders
      }
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
