import { AUDIO, IMAGE } from "~/constants/media"
import MediaService from "~/data/media-service"
import type { AudioDetail, ImageDetail } from "~/types/media"
import { createApiService } from "~/data/api-service"

export const initServices = {
  [AUDIO]: (accessToken?: string) =>
    new MediaService<AudioDetail>(createApiService({ accessToken }), AUDIO),
  [IMAGE]: (accessToken?: string) =>
    new MediaService<ImageDetail>(createApiService({ accessToken }), IMAGE),
}
