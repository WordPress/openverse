import { AUDIO, IMAGE } from "~/constants/media"
import type { AudioDetail, ImageDetail, Media } from "~/types/media"
import { ApiService, createApiService } from "~/data/api-service"
import type { MediaProvider } from "~/types/media-provider"

export class MediaProviderService<T extends Media> {
  private readonly apiService: ApiService
  private readonly mediaType: T["frontendMediaType"]

  constructor(apiService: ApiService, mediaType: T["frontendMediaType"]) {
    this.apiService = apiService
    this.mediaType = mediaType
  }

  /**
   * Implements an endpoint to get audio provider statistics.
   * SSR-called
   */
  async getProviderStats(): Promise<{ data: MediaProvider[] }> {
    return await this.apiService.get(this.mediaType, "stats")
  }
}

export const initProviderServices = {
  [AUDIO]: (accessToken?: string) =>
    new MediaProviderService<AudioDetail>(
      createApiService({ accessToken }),
      AUDIO
    ),
  [IMAGE]: (accessToken?: string) =>
    new MediaProviderService<ImageDetail>(
      createApiService({ accessToken }),
      IMAGE
    ),
}
