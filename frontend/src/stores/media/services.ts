import { AUDIO, IMAGE } from "~/constants/media"
import MediaService from "~/data/media-service"
import { createApiService } from "~/data/api-service"

export const initServices = {
  [AUDIO]: (accessToken?: string) =>
    new MediaService<typeof AUDIO>(createApiService({ accessToken }), AUDIO),
  [IMAGE]: (accessToken?: string) =>
    new MediaService<typeof IMAGE>(createApiService({ accessToken }), IMAGE),
}
