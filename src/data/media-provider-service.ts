import { AUDIO, IMAGE, SupportedMediaType } from '~/constants/media'
import { VersionedApiService } from '~/data/api-service'
import type { MediaProvider } from '~/models/media-provider'

/**
 * Service that calls API to get Media Provider stats
 * @param mediaType - the media type of the provider.
 */
export const MediaProviderService = (mediaType: SupportedMediaType) => ({
  /**
   * Implements an endpoint to get audio provider statistics.
   * SSR-called
   */
  getProviderStats: async (): Promise<{ data: MediaProvider[] }> => {
    return await VersionedApiService.get(mediaType, 'stats')
  },
})

export const providerServices = {
  [AUDIO]: MediaProviderService(AUDIO),
  [IMAGE]: MediaProviderService(IMAGE),
} as const
