// This module contains types and interfaces for media items.
//
// The source code of this package is parsed to create the media properties
// documentation by the script `scripts/document-media.js`.

import type { SupportedMediaType } from "~/constants/media"
import type { License, LicenseVersion } from "~/constants/license"
import {
  SENSITIVITY_RESPONSE_PARAM,
  Sensitivity,
} from "~/constants/content-safety"
import { AUDIO, IMAGE } from "~/constants/media"

export interface Tag {
  name: string
}

/**
 * Stores properties common to all media items. This is extended by interfaces
 * for individual media.
 */
export interface Media {
  /**
   * the UUID4 identifier of the media item
   *
   * @see {@link https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)|UUID4}
   */
  id: string
  /**
   * the name of the creative work; This involves the following kinds of
   * changes to the original title:
   *
   * - remove the file extension
   * - escape HTML
   * - handle empty titles
   */
  title: string
  /** the raw name of the creative work, as returned by the API */
  originalTitle: string

  creator?: string
  creator_url?: string

  url: string
  foreign_landing_url: string

  license: License
  license_version: LicenseVersion
  license_url?: string
  attribution: string

  frontendMediaType: SupportedMediaType

  description?: string

  category: string | null
  provider: string
  source: string
  providerName: string
  sourceName: string
  thumbnail?: string

  filesize?: string
  filetype?: string

  detail_url: string
  related_url: string

  tags: Tag[]
  fields_matched?: string[]

  sensitivity: Sensitivity[]
  isSensitive: boolean
}

export interface ImageDetail extends Media {
  frontendMediaType: "image"

  /** the vertical length of the image in pixels */
  height?: number
  /** the horizontal length of the image in pixels */
  width?: number
}

export interface AudioSet {
  title: string
  foreign_landing_url: string
  creator?: string
  creator_url?: string
  url?: string
  filesize?: number
  filetype?: string
}

export interface AudioDetail extends Media {
  frontendMediaType: "audio"

  audio_set?: AudioSet
  genres?: string[]
  length?: string
  /** the time period of the track in milliseconds */
  duration?: number
  /**
   * amount of digital audio data transmitted or processed in unit time; This
   * field holds numbers measured in bits per second.
   *
   * @see {@link https://en.wikipedia.org/wiki/Bit_rate#Audio|Wikipedia}
   */
  bit_rate?: number
  /**
   * number of samples for digital representation taken in unit time; This field
   * holds numbers measured in hertz.
   *
   * @see {@link https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Audio_sampling|Wikipedia}
   */
  sample_rate?: number
  alt_files?: { provider: string; filetype: string }[]
  peaks?: number[]
  waveform?: string

  // Set and managed by the frontend client-side
  hasLoaded?: boolean
}

export type DetailFromMediaType<T extends SupportedMediaType> =
  T extends "audio" ? AudioDetail : ImageDetail

/**
 * This interface is a subset of `Media` that types dictionaries sent by the API
 * being decoded in the `decodeMediaData` function.
 */
export interface ApiMedia
  extends Omit<
    Media,
    | "frontendMediaType"
    | "title"
    | "originalTitle"
    | "isSensitive"
    | "sensitivity"
    | "sourceName"
    | "providerName"
  > {
  title?: string
  originalTitle?: string
  [SENSITIVITY_RESPONSE_PARAM]?: Sensitivity[]
}

export interface ImageDimensions {
  width?: number
  height?: number
}

export type AspectRatio = "square" | "intrinsic"

export const isDetail = {
  audio: (media: Media | null): media is AudioDetail =>
    isMediaDetail(media, AUDIO),
  image: (media: Media | null): media is ImageDetail =>
    isMediaDetail(media, IMAGE),
}

export const isMediaDetail = <T extends SupportedMediaType>(
  media: Media | null,
  mediaType: T
): media is DetailFromMediaType<T> => {
  return !!media && media.frontendMediaType === mediaType
}

export type Metadata = {
  name?: string
  label: string
  url?: string
  value: string
  source?: string
}
