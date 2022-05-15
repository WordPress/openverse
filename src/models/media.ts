import type { SupportedMediaType } from '~/constants/media'
import type { License, LicenseVersion } from '~/constants/license'

export interface Tag {
  name: string
}

/**
 * Stores properties common to all media items. This is extended by interfaces
 * for individual media.
 */
export interface Media {
  id: string
  title: string

  creator?: string
  creator_url?: string

  url: string
  foreign_landing_url: string

  license: License
  license_version: LicenseVersion
  license_url?: string
  attribution: string

  frontendMediaType: SupportedMediaType

  category: string | null
  provider: string
  source?: string
  providerName?: string
  sourceName?: string
  thumbnail?: string

  filesize?: string
  filetype?: string

  detail_url: string
  related_url: string

  tags: Tag[]
  fields_matched?: string[]
}

export interface ImageDetail extends Media {
  frontendMediaType: 'image'

  height?: number
  width?: number
}

export interface AudioDetail extends Media {
  frontendMediaType: 'audio'

  audio_set?: string
  genres?: string[]
  duration?: number
  bit_rate?: number
  sample_rate?: number
  alt_files?: { provider: string; filetype: string }[]
  peaks?: number[]
  waveform?: string
}

export type DetailFromMediaType<T extends SupportedMediaType> =
  T extends 'audio' ? AudioDetail : ImageDetail
