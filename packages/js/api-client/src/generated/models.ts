/**
 * This file is generated from a template. Do not edit it by hand!
 *
 * @see {@link https://docs.openverse.org/packages/js/api-client/index.html#development-and-implementation-details}
 */

export type GrantTypeEnum = "client_credentials"

export interface OAuth2KeyInfo {
  /**
   * The number of requests your key has performed in the last minute.
   */
  requests_this_minute: null | number

  /**
   * The number of requests your key has performed in the last day.
   */
  requests_today: null | number

  /**
   * The type of rate limit applied to your key. Can be 'standard' or 'enhanced'; enhanced users enjoy higher rate limits than their standard key counterparts. Contact Openverse if you need a higher rate limit.
   */
  rate_limit_model: string

  /**
   * Whether the application has verified the submitted email address.
   */
  verified: boolean
}

/**
 * Serializes the response for an access token.
 *
 * This is a dummy serializer for OpenAPI and is not actually used.
 */
export interface OAuth2Token {
  /**
   * The access token that can be used to authenticate requests.
   */
  access_token: string

  /**
   * The type of token. This will always be 'Bearer'.
   */
  token_type: string

  /**
   * The number of seconds until the token expires.
   */
  expires_in: number

  /**
   * The scope of the token.
   */
  scope: string
}

export interface OAuth2Registration {
  /**
   * A unique human-readable name for your application or project requiring access to the Openverse API.
   */
  name: string

  /**
   * A description of what you are trying to achieve with your project using the API. Please provide as much detail as possible!
   */
  description: string

  /**
   * A valid email that we can reach you at if we have any questions about your use case or data consumption.
   */
  email: string
}

export interface OAuth2Application {
  /**
   * The unique, public identifier of your application.
   */
  client_id: string

  /**
   * The secret key used to authenticate your application.
   */
  client_secret: string

  /**
   * The name of your application or project.
   */
  name: string

  /**
   * Some additional information about the application.
   */
  msg: string
}

/**
 * Serializes a request for an access token.
 *
 * This is a dummy serializer for OpenAPI and is not actually used.
 */
export interface OAuth2TokenRequest {
  /**
   * The unique, public identifier of your application.
   */
  client_id: string

  /**
   * The secret key used to authenticate your application.
   */
  client_secret: string

  grant_type: "client_credentials"
}

export interface Source {
  /**
   * The source of the media, e.g. flickr
   */
  source_name: string

  /**
   * The name of content source, e.g. Flickr
   */
  display_name: string

  /**
   * The URL of the source, e.g. https://www.flickr.com
   */
  source_url: string

  /**
   * The URL to a logo for the source.
   */
  logo_url: null | string

  /**
   * The number of media items indexed from the source.
   */
  media_count: number
}

/**
 * This output serializer serializes a singular tag.
 */
export interface Tag {
  /**
   * The name of a detailed tag.
   */
  name: string

  /**
   * The accuracy of a machine-generated tag. Human-generated tags have a null accuracy field.
   */
  accuracy?: null | number

  /**
   * The source of the tag. When this field matches the provider for the record, the tag originated from the upstream provider. Otherwise, the tag was added with an external machine-generated labeling processes.
   */
  unstable__provider: null | string
}

/**
 * A set of alternative files for a single audio object,
 * rendered as a part of the `AudioSerializer` output.
 */
export interface AudioAltFile {
  /**
   * URL of the alternative file.
   */
  url: string

  /**
   * Bit rate of the alternative file.
   */
  bit_rate?: number

  /**
   * Size of the alternative file in bytes.
   */
  filesize?: number

  /**
   * File type of the alternative file.
   */
  filetype: string

  /**
   * Sample rate of the alternative file.
   */
  sample_rate?: number
}

/**
 * An audio set, rendered as a part of the `AudioSerializer` output.
 */
export interface AudioSet {
  /**
   * The name of the media.
   */
  title?: null | string

  /**
   * The landing page of the work.
   */
  foreign_landing_url?: null | string

  /**
   * The name of the media creator.
   */
  creator?: null | string

  /**
   * A direct link to the media creator.
   */
  creator_url?: null | string

  /**
   * The actual URL to the media file.
   */
  url?: null | string

  /**
   * Number in bytes, e.g. 1024.
   */
  filesize?: null | number

  /**
   * The type of the file, related to the file extension.
   */
  filetype?: null | string
}

export interface AudioWaveform {
  len: number

  points: Array<number>
}

/**
 * A single audio file. Used in search results.
 */
export interface Audio {
  /**
   * Our unique identifier for an open-licensed work.
   */
  id: string

  /**
   * The name of the media.
   */
  title?: null | string

  /**
   * The timestamp of when the media was indexed by Openverse.
   */
  indexed_on: string

  /**
   * The landing page of the work.
   */
  foreign_landing_url?: null | string

  /**
   * The actual URL to the media file.
   */
  url?: null | string

  /**
   * The name of the media creator.
   */
  creator?: null | string

  /**
   * A direct link to the media creator.
   */
  creator_url?: null | string

  /**
   * The name of license for the media.
   */
  license: string

  /**
   * The version of the media license.
   */
  license_version?: null | string

  /**
   * A direct link to the license deed or legal terms.
   */
  license_url: null | string

  /**
   * The content provider, e.g. Flickr, Jamendo...
   */
  provider?: null | string

  /**
   * The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr.
   */
  source?: null | string

  /**
   * The top-level classification of this media file.
   */
  category?: null | string

  /**
   * An array of audio genres such as `rock`, `electronic` for `music` category, or `politics`, `sport`, `education` for `podcast` category
   */
  genres?: null | Array<string>

  /**
   * Number in bytes, e.g. 1024.
   */
  filesize?: null | number

  /**
   * The type of the file, related to the file extension.
   */
  filetype?: null | string

  /**
   * Tags with detailed metadata, such as accuracy.
   */
  tags: null | Array<Tag>

  /**
   * JSON describing alternative files for this audio.
   */
  alt_files: null | Array<AudioAltFile>

  /**
   * Legally valid attribution for the media item in plain-text English.
   */
  attribution: null | string

  /**
   * List the fields that matched the query for this result.
   */
  fields_matched: null | Array<unknown>

  /**
   * Whether the media item is marked as mature
   */
  mature: boolean

  /**
   * Reference to set of which this track is a part.
   */
  audio_set: null | AudioSet

  /**
   * The time length of the audio file in milliseconds.
   */
  duration?: null | number

  /**
   * Number in bits per second, eg. 128000.
   */
  bit_rate?: null | number

  /**
   * Number in hertz, eg. 44100.
   */
  sample_rate?: null | number

  /**
   * A direct link to the miniature artwork.
   */
  thumbnail: null | string

  /**
   * A direct link to the detail view of this audio file.
   */
  detail_url: string

  /**
   * A link to an endpoint that provides similar audio files.
   */
  related_url: string

  /**
   * A direct link to the waveform peaks.
   */
  waveform: string
}

/**
 * A single image. Used in search results.
 */
export interface Image {
  /**
   * Our unique identifier for an open-licensed work.
   */
  id: string

  /**
   * The name of the media.
   */
  title?: null | string

  /**
   * The timestamp of when the media was indexed by Openverse.
   */
  indexed_on: string

  /**
   * The landing page of the work.
   */
  foreign_landing_url?: null | string

  /**
   * The actual URL to the media file.
   */
  url?: null | string

  /**
   * The name of the media creator.
   */
  creator?: null | string

  /**
   * A direct link to the media creator.
   */
  creator_url?: null | string

  /**
   * The name of license for the media.
   */
  license: string

  /**
   * The version of the media license.
   */
  license_version?: null | string

  /**
   * A direct link to the license deed or legal terms.
   */
  license_url: null | string

  /**
   * The content provider, e.g. Flickr, Jamendo...
   */
  provider?: null | string

  /**
   * The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr.
   */
  source?: null | string

  /**
   * The top-level classification of this media file.
   */
  category?: null | string

  /**
   * Number in bytes, e.g. 1024.
   */
  filesize?: null | number

  /**
   * The type of the file, related to the file extension.
   */
  filetype?: null | string

  /**
   * Tags with detailed metadata, such as accuracy.
   */
  tags: null | Array<Tag>

  /**
   * Legally valid attribution for the media item in plain-text English.
   */
  attribution: null | string

  /**
   * List the fields that matched the query for this result.
   */
  fields_matched: null | Array<unknown>

  /**
   * Whether the media item is marked as mature
   */
  mature: boolean

  /**
   * The height of the image in pixels. Not always available.
   */
  height?: null | number

  /**
   * The width of the image in pixels. Not always available.
   */
  width?: null | number

  /**
   * A direct link to the miniature artwork.
   */
  thumbnail: string

  /**
   * A direct link to the detail view of this audio file.
   */
  detail_url: string

  /**
   * A link to an endpoint that provides similar audio files.
   */
  related_url: string
}

export interface PaginatedImageList {
  /**
   * The total number of items returned by search result.
   */
  result_count: number

  /**
   * The total number of pages returned by search result.
   */
  page_count: number

  /**
   * The number of items per page.
   */
  page_size: number

  /**
   * The current page number returned in the response.
   */
  page: number

  results: Array<Image>

  /**
   * Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
   */
  warnings?: Array<unknown>
}

export interface PaginatedAudioList {
  /**
   * The total number of items returned by search result.
   */
  result_count: number

  /**
   * The total number of pages returned by search result.
   */
  page_count: number

  /**
   * The number of items per page.
   */
  page_size: number

  /**
   * The current page number returned in the response.
   */
  page: number

  results: Array<Audio>

  /**
   * Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
   */
  warnings?: Array<unknown>
}
