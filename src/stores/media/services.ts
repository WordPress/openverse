import { AUDIO, IMAGE } from '~/constants/media'
import MediaService from '~/data/media-service'
import type { AudioDetail, ImageDetail } from '~/models/media'

export const services = {
  [AUDIO]: new MediaService<AudioDetail>(AUDIO),
  [IMAGE]: new MediaService<ImageDetail>(IMAGE),
} as const
