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
  /** The raw name of the creative work, as returned by the API. */
  originalTitle: string
  /** The text name, handle, or username of the author of the creative work. */
  creator?: string
  /** A URL to the creator's profile on the provider or other personal webpage, depending on the provider. */
  creator_url?: string
  /** A URL pointing to the actual media file on the provider. */
  url: string
  /**
   * A URL to the page where the media item is hosted on the foreign provider's site.
   * This is often used to give credit to the original source or for users to find more information.
   */
  foreign_landing_url: string
  /** The code of the open copy-left license assigned to the work. */
  license: License
  /** The version number of the Creative Commons license as a string, or an empty string. */
  license_version: LicenseVersion
  /** A link to the landing page of the License, typically the deed or another informational page. */
  license_url?: string
  /** The full text to properly attribute the work to the creator. */
  attribution: string

  frontendMediaType: SupportedMediaType

  /** A long test describing the media, from the provider. */
  description?: string

  category: string | null
  provider: string
  source: string
  providerName: string
  sourceName: string
  /**
   * A URL to a thumbnail image of the media.
   *
   * Typically album art for an audio track, or
   * a minified thumbnail for image works.
   */
  thumbnail?: string

  filesize?: string
  filetype?: string

  detail_url: string
  /** The API URL which provides a list of related media results. */
  related_url: string

  tags: Tag[]

  /** An array of field names that matched the search query. */
  fields_matched?: string[]

  /**
   * An array of sensitivity markers.
   * These markers indicate various sensitivity or content warning categories applicable to the media.
   */
  sensitivity: Sensitivity[]

  /**
   * Indicates if the media is marked as sensitive.
   * If true, the media has sensitivity markers that might require user discretion or warnings.
   */
  isSensitive: boolean
}

export interface ImageDetail extends Media {
  frontendMediaType: "image"
  /** the vertical length of the image, in pixels. */
  height?: number
  /** The horizontal length of the image, in pixels. */
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
  /** An object representing a group of audio tracks this track belongs to, like an album or podcast. */
  audio_set?: AudioSet
  /** A raw list of strings representing musical genres. */
  genres?: string[]
  length?: string
  /**
   * The time period of the track in milliseconds.
   * This provides the duration of the audio track in a numerical format.
   */
  duration?: number
  /**
   * Amount of digital audio data transmitted or processed in unit time;
   * This field holds numbers measured in bits per second (bps).
   *
   * @see {@link https://en.wikipedia.org/wiki/Bit_rate#Audio|Wikipedia}
   */
  bit_rate?: number

  /**
   * Number of samples for digital representation taken in unit time;
   * This field holds numbers measured in hertz (Hz).
   *
   * @see {@link https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Audio_sampling|Wikipedia}
   */
  sample_rate?: number
  /**
   * An array of alternative files of different filetypes.
   * This can include different formats of the audio track for compatibility and quality options.
   */
  alt_files?: { provider: string; filetype: string }[]
  /** An array of peak amplitude values used to generate a visual representation of the audio waveform. */
  peaks?: number[]
  /** The URL of the API `/wavepoint` endpoint for the audio track. This endpoint provides the full peaks array for the track.  */
  waveform?: string
  /**
   * Set and managed by the frontend client-side to indicate if the audio has been fully loaded.
   * Useful for managing UI elements based on the loading state of the audio.
   */
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
