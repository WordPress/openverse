/**
 * This file is generated from a template. Do not edit it by hand!
 *
 * @see {@link https://docs.openverse.org/packages/js/api-client/index.html#development-and-implementation-details}
 */

/* eslint-disable @typescript-eslint/no-unused-vars */
import type {
  OAuth2KeyInfo,
  OAuth2Token,
  OAuth2Registration,
  OAuth2Application,
  OAuth2TokenRequest,
  Source,
  Tag,
  AudioAltFile,
  AudioSet,
  AudioWaveform,
  Audio,
  Image,
  PaginatedImageList,
  PaginatedAudioList,
} from "./models"
/* eslint-enable @typescript-eslint/no-unused-vars */

export type Routes = {
  /**
   * Return audio files that match the query.
   *
   * This endpoint allows you to search within specific fields, or to retrieve
   * a collection of all audio files from a specific source, creator or tag.
   * Results are paginated on the basis of the `page` parameter. The `page_size`
   * parameter controls the total number of pages.
   *
   * Although there may be millions of relevant records, only the most relevant
   * or the most recent several thousand records can be viewed. This is by design:
   * the search endpoint should be used to find the top 10,000 most relevant
   * results, not for exhaustive search or bulk download of every barely relevant
   * result. As such, the caller should not try to access pages beyond `page_count`,
   * or else the server will reject the query.
   *
   * ### Default search
   * The **default search** allows users to find media based on a query string.
   * It supports a wide range of optional filters to narrow down search results
   * according to specific needs.
   *
   * By default, this endpoint performs a full-text search for the value of `q` parameter.
   * You can search within the `creator`, `title` or `tags` fields by omitting
   * the `q` parameter and using one of these field parameters.
   * These results can be filtered by `source`, `excluded_source`, `license`, `license_type`, `creator`, `tags`, `title`, `filter_dead`, `extension`, `mature`, `unstable__include_sensitive_results`, `category` and `length`.
   *
   * The default search results are sorted by relevance.
   *
   * ### Collection search
   * The collection search allows to retrieve a collection of media from a specific source,
   * creator or tag. The `unstable__collection` parameter is used to specify the type of collection to retrieve.
   *
   * - `unstable__collection=tag&unstable__tag=tagName` will return the media with tag `tagName`.
   * - `unstable__collection=source&source=sourceName` will return the media from source `sourceName`.
   * - `unstable__collection=creator&creator=creatorName&source=sourceName` will return the media by creator `creatorName` at `sourceName`.
   *
   * Collection results are sorted by the time they were added to Openverse, with the most recent
   * additions appearing first. The filters such as `license` are not available for collections.
   */
  "GET /v1/audio/": {
    request: {
      params?: {
        /**
         * The page of results to retrieve. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth).
         */
        page?: number
        /**
         * Number of results to return per page. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth).
         */
        page_size?: number
        /**
         * A query string that should not exceed 200 characters in length
         */
        q?: string
        /**
         * For default search, a comma separated list of data sources.
         * When the `unstable__collection` parameter is used, this parameter only accepts a single source.
         *
         * Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/audio/stats/.
         */
        source?: string
        /**
         * A comma separated list of data sources to exclude from the search.
         * Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/audio/stats/.
         */
        excluded_source?: string
        /**
         * Search by tag only. Cannot be used with `q`. The search is fuzzy, so `tags=cat` will match any value that includes the word `cat`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma.
         */
        tags?: string
        /**
         * Search by title only. Cannot be used with `q`. The search is fuzzy, so `title=photo` will match any value that includes the word `photo`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma.
         */
        title?: string
        /**
         * _When `q` parameter is present, `creator` parameter is ignored._
         *
         * **Creator collection**
         * When used with `unstable__collection=creator&source=sourceName`, returns the collection of media
         * by the specified creator. Notice that a single creator's media items
         * can be found on several sources, but this collection only returns the
         * items from the specified source.
         * This is why for this collection, both the creator and the source
         * parameters are required, and matched exactly. For a fuzzy creator search,
         * use the default search without the `unstable__collection` parameter.
         *
         * **Creator search**
         * When used without the `unstable__collection` parameter, will search in the creator field only.
         * The search is fuzzy, so `creator=john` will match any value that includes the
         * word `john`. If the value contains space, items that contain any of
         * the words in the value will match. To search for several values,
         * join them with a comma.
         */
        creator?: string
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         *
         * The kind of media collection to return.
         *
         * Must be used with `unstable__tag`, `source` or `creator`+`source`
         *
         * * `tag` - tag
         * * `source` - source
         * * `creator` - creator
         */
        unstable__collection?: "tag" | "source" | "creator"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         *
         * _Must be used with `unstable__collection=tag`_
         *
         * Get the collection of media with a specific tag. Returns the collection of media
         * that has the specified tag, matching exactly and entirely.
         *
         * Differences that will cause tags to not match are:
         * - upper and lower case letters
         * - diacritical marks
         * - hyphenation
         * - spacing
         * - multi-word tags where the query is only one of the words in the tag
         * - multi-word tags where the words are in a different order.
         *
         * Examples of tags that **do not** match:
         * - "Low-Quality" and "low-quality"
         * - "jalapeño" and "jalapeno"
         * - "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
         * - "dog walking" and "dog  walking" (where the latter has two spaces between the
         * last two words, as in a typographical error)
         * - "runner" and "marathon runner"
         * - "exclaiming loudly" and "loudly exclaiming"
         *
         * For non-exact or multi-tag matching, using the `tags` query parameter.
         */
        unstable__tag?: string
        /**
         * A comma separated list of licenses; available licenses include: `by`, `by-nc`, `by-nc-nd`, `by-nc-sa`, `by-nd`, `by-sa`, `cc0`, `nc-sampling+`, `pdm`, and `sampling+`.
         */
        license?: string
        /**
         * A comma separated list of license types; available license types include: `all`, `all-cc`, `commercial`, and `modification`.
         */
        license_type?: string
        /**
         * Control whether 404 links are filtered out.
         */
        filter_dead?: boolean
        /**
         * A comma separated list of desired file extensions.
         */
        extension?: string
        /**
         * Whether to include sensitive content.
         */
        mature?: boolean
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The field which should be the basis for sorting results.
         *
         * * `relevance` - Relevance
         * * `indexed_on` - Indexing date
         */
        unstable__sort_by?: "relevance" | "indexed_on"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The direction of sorting. Cannot be applied when sorting by `relevance`.
         *
         * * `desc` - Descending
         * * `asc` - Ascending
         */
        unstable__sort_dir?: "desc" | "asc"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * If enabled, the search will add a boost to results that are from authoritative sources.
         */
        unstable__authority?: boolean
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The boost coefficient to apply to authoritative sources, multiplied with the popularity boost.
         */
        unstable__authority_boost?: number
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * Whether to include results considered sensitive.
         */
        unstable__include_sensitive_results?: boolean
        /**
         * A comma separated list of categories; available categories include: `audiobook`, `music`, `news`, `podcast`, `pronunciation`, and `sound_effect`.
         */
        category?: string
        /**
         * A comma separated list of lengths; available lengths include: `long`, `medium`, `short`, and `shortest`.
         */
        length?: string
        /**
         * Whether to include the waveform peaks or not
         */
        peaks?: boolean
      }
    }
    response: PaginatedAudioList
  }

  /**
   * Get the details of a specified audio track.
   *
   * By using this endpoint, you can obtain info about audio files such as
   * `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `genres`, `filesize`, `filetype`, `tags`, `alt_files`, `attribution`, `fields_matched`, `mature`, `audio_set`, `duration`, `bit_rate`, `sample_rate`, `thumbnail`, `detail_url`, `related_url`, `waveform`, `peaks` and `unstable__sensitivity`
   */
  "GET /v1/audio/{identifier}/": {
    request: {
      identifier: string
    }
    response: Audio
  }

  /**
   * Get related audio files for a specified audio track.
   *
   * By using this endpoint, you can get the details of related audio such as
   * `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `genres`, `filesize`, `filetype`, `tags`, `alt_files`, `attribution`, `fields_matched`, `mature`, `audio_set`, `duration`, `bit_rate`, `sample_rate`, `thumbnail`, `detail_url`, `related_url`, `waveform`, `peaks` and `unstable__sensitivity`.
   */
  "GET /v1/audio/{identifier}/related/": {
    request: {
      identifier: string
    }
    response: PaginatedAudioList
  }

  /**
   * Retrieve the scaled down and compressed thumbnail of the artwork of an
   * audio track or its audio set.
   */
  "GET /v1/audio/{identifier}/thumb/": {
    request: {
      identifier: string
      params?: {
        /**
         * whether to render the actual image and not a thumbnail version
         */
        full_size?: boolean
        /**
         * whether to compress the output image to reduce file size,defaults to opposite of `full_size`
         */
        compressed?: boolean
      }
    }
    response: ReadableStream
  }

  /**
   * Get the waveform peaks for an audio track.
   *
   * The peaks are provided as a list of numbers, each of these numbers being
   * a fraction between 0 and 1. The list contains approximately 1000 numbers,
   * although it can be slightly higher or lower, depending on the track's length.
   */
  "GET /v1/audio/{identifier}/waveform/": {
    request: {
      identifier: string
    }
    response: AudioWaveform
  }

  /**
   * Get a list of all content sources and their respective number of
   * audio files in the Openverse catalog.
   *
   * By using this endpoint, you can obtain info about content sources such
   * as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`.
   */
  "GET /v1/audio/stats/": {
    request: unknown
    response: Array<Source>
  }

  /**
   * Register an application to access to API via OAuth2.
   *
   * Upon registering, you will receive a `client_id` and `client_secret`,
   * which you can then use to authenticate using the standard OAuth2 flow.
   *
   * \> ⚠️ **WARNINGS:**
   * \> - Store your `client_id` and `client_secret` because you will not be
   * \>   able to retrieve them later.
   * \> - You must keep `client_secret` confidential, as anybody with your
   * \>   `client_secret` can impersonate your application.
   *
   * You must verify your email address by click the link sent to you in an
   * email. Until you do that, the application will be subject to the same
   * rate limits as an anonymous user.
   */
  "POST /v1/auth_tokens/register/": {
    request: {
      body: OAuth2Registration
    }
    response: OAuth2Application
  }

  /**
   * Get an access token using client credentials.
   *
   * To authenticate your requests to the Openverse API, you need to provide
   * an access token as a bearer token in the `Authorization` header of your
   * requests. This endpoint takes your client ID and secret, and issues an
   * access token.
   *
   * \> **NOTE:** This endpoint only accepts data as
   * \> `application/x-www-form-urlencoded`. Any other encoding will not work.
   *
   * Once your access token expires, you can request another one from this
   * endpoint.
   */
  "POST /v1/auth_tokens/token/": {
    request: {
      body: OAuth2TokenRequest
    }
    response: OAuth2Token
  }

  /**
   * Return images that match the query.
   *
   * This endpoint allows you to search within specific fields, or to retrieve
   * a collection of all images from a specific source, creator or tag.
   * Results are paginated on the basis of the `page` parameter. The `page_size`
   * parameter controls the total number of pages.
   *
   * Although there may be millions of relevant records, only the most relevant
   * or the most recent several thousand records can be viewed. This is by design:
   * the search endpoint should be used to find the top 10,000 most relevant
   * results, not for exhaustive search or bulk download of every barely relevant
   * result. As such, the caller should not try to access pages beyond `page_count`,
   * or else the server will reject the query.
   *
   * ### Default search
   * The **default search** allows users to find media based on a query string.
   * It supports a wide range of optional filters to narrow down search results
   * according to specific needs.
   *
   * By default, this endpoint performs a full-text search for the value of `q` parameter.
   * You can search within the `creator`, `title` or `tags` fields by omitting
   * the `q` parameter and using one of these field parameters.
   * These results can be filtered by `source`, `excluded_source`, `license`, `license_type`, `creator`, `tags`, `title`, `filter_dead`, `extension`, `mature`, `unstable__include_sensitive_results`, `category`, `aspect_ratio` and `size`.
   *
   * The default search results are sorted by relevance.
   *
   * ### Collection search
   * The collection search allows to retrieve a collection of media from a specific source,
   * creator or tag. The `unstable__collection` parameter is used to specify the type of collection to retrieve.
   *
   * - `unstable__collection=tag&unstable__tag=tagName` will return the media with tag `tagName`.
   * - `unstable__collection=source&source=sourceName` will return the media from source `sourceName`.
   * - `unstable__collection=creator&creator=creatorName&source=sourceName` will return the media by creator `creatorName` at `sourceName`.
   *
   * Collection results are sorted by the time they were added to Openverse, with the most recent
   * additions appearing first. The filters such as `license` are not available for collections.
   */
  "GET /v1/images/": {
    request: {
      params?: {
        /**
         * The page of results to retrieve. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth).
         */
        page?: number
        /**
         * Number of results to return per page. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth).
         */
        page_size?: number
        /**
         * A query string that should not exceed 200 characters in length
         */
        q?: string
        /**
         * For default search, a comma separated list of data sources.
         * When the `unstable__collection` parameter is used, this parameter only accepts a single source.
         *
         * Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/images/stats/.
         */
        source?: string
        /**
         * A comma separated list of data sources to exclude from the search.
         * Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/images/stats/.
         */
        excluded_source?: string
        /**
         * Search by tag only. Cannot be used with `q`. The search is fuzzy, so `tags=cat` will match any value that includes the word `cat`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma.
         */
        tags?: string
        /**
         * Search by title only. Cannot be used with `q`. The search is fuzzy, so `title=photo` will match any value that includes the word `photo`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma.
         */
        title?: string
        /**
         * _When `q` parameter is present, `creator` parameter is ignored._
         *
         * **Creator collection**
         * When used with `unstable__collection=creator&source=sourceName`, returns the collection of media
         * by the specified creator. Notice that a single creator's media items
         * can be found on several sources, but this collection only returns the
         * items from the specified source.
         * This is why for this collection, both the creator and the source
         * parameters are required, and matched exactly. For a fuzzy creator search,
         * use the default search without the `unstable__collection` parameter.
         *
         * **Creator search**
         * When used without the `unstable__collection` parameter, will search in the creator field only.
         * The search is fuzzy, so `creator=john` will match any value that includes the
         * word `john`. If the value contains space, items that contain any of
         * the words in the value will match. To search for several values,
         * join them with a comma.
         */
        creator?: string
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         *
         * The kind of media collection to return.
         *
         * Must be used with `unstable__tag`, `source` or `creator`+`source`
         *
         * * `tag` - tag
         * * `source` - source
         * * `creator` - creator
         */
        unstable__collection?: "tag" | "source" | "creator"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         *
         * _Must be used with `unstable__collection=tag`_
         *
         * Get the collection of media with a specific tag. Returns the collection of media
         * that has the specified tag, matching exactly and entirely.
         *
         * Differences that will cause tags to not match are:
         * - upper and lower case letters
         * - diacritical marks
         * - hyphenation
         * - spacing
         * - multi-word tags where the query is only one of the words in the tag
         * - multi-word tags where the words are in a different order.
         *
         * Examples of tags that **do not** match:
         * - "Low-Quality" and "low-quality"
         * - "jalapeño" and "jalapeno"
         * - "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
         * - "dog walking" and "dog  walking" (where the latter has two spaces between the
         * last two words, as in a typographical error)
         * - "runner" and "marathon runner"
         * - "exclaiming loudly" and "loudly exclaiming"
         *
         * For non-exact or multi-tag matching, using the `tags` query parameter.
         */
        unstable__tag?: string
        /**
         * A comma separated list of licenses; available licenses include: `by`, `by-nc`, `by-nc-nd`, `by-nc-sa`, `by-nd`, `by-sa`, `cc0`, `nc-sampling+`, `pdm`, and `sampling+`.
         */
        license?: string
        /**
         * A comma separated list of license types; available license types include: `all`, `all-cc`, `commercial`, and `modification`.
         */
        license_type?: string
        /**
         * Control whether 404 links are filtered out.
         */
        filter_dead?: boolean
        /**
         * A comma separated list of desired file extensions.
         */
        extension?: string
        /**
         * Whether to include sensitive content.
         */
        mature?: boolean
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The field which should be the basis for sorting results.
         *
         * * `relevance` - Relevance
         * * `indexed_on` - Indexing date
         */
        unstable__sort_by?: "relevance" | "indexed_on"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The direction of sorting. Cannot be applied when sorting by `relevance`.
         *
         * * `desc` - Descending
         * * `asc` - Ascending
         */
        unstable__sort_dir?: "desc" | "asc"
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * If enabled, the search will add a boost to results that are from authoritative sources.
         */
        unstable__authority?: boolean
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * The boost coefficient to apply to authoritative sources, multiplied with the popularity boost.
         */
        unstable__authority_boost?: number
        /**
         * _Caution: Parameters prefixed with `unstable__` are experimental and
         * may change or be removed without notice in future updates. Use them
         * with caution as they are not covered by our API versioning policy._
         *
         *
         * Whether to include results considered sensitive.
         */
        unstable__include_sensitive_results?: boolean
        /**
         * A comma separated list of categories; available categories include: `digitized_artwork`, `illustration`, and `photograph`.
         */
        category?: string
        /**
         * A comma separated list of aspect ratios; available aspect ratios include: `square`, `tall`, and `wide`.
         */
        aspect_ratio?: string
        /**
         * A comma separated list of image sizes; available image sizes include: `large`, `medium`, and `small`.
         */
        size?: string
      }
    }
    response: PaginatedImageList
  }

  /**
   * Get the details of a specified image.
   *
   * By using this endpoint, you can obtain info about images such as
   * `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `filesize`, `filetype`, `tags`, `attribution`, `fields_matched`, `mature`, `height`, `width`, `thumbnail`, `detail_url`, `related_url` and `unstable__sensitivity`
   */
  "GET /v1/images/{identifier}/": {
    request: {
      identifier: string
    }
    response: Image
  }

  /**
   * Get related images for a specified image.
   *
   * By using this endpoint, you can get the details of related images such as
   * `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `filesize`, `filetype`, `tags`, `attribution`, `fields_matched`, `mature`, `height`, `width`, `thumbnail`, `detail_url`, `related_url` and `unstable__sensitivity`.
   */
  "GET /v1/images/{identifier}/related/": {
    request: {
      identifier: string
    }
    response: Image
  }

  /**
   * Retrieve the scaled down and compressed thumbnail of the image.
   */
  "GET /v1/images/{identifier}/thumb/": {
    request: {
      identifier: string
      params?: {
        /**
         * whether to render the actual image and not a thumbnail version
         */
        full_size?: boolean
        /**
         * whether to compress the output image to reduce file size,defaults to opposite of `full_size`
         */
        compressed?: boolean
      }
    }
    response: ReadableStream
  }

  /**
   * Get a list of all content sources and their respective number of
   * images in the Openverse catalog.
   *
   * By using this endpoint, you can obtain info about content sources such
   * as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`.
   */
  "GET /v1/images/stats/": {
    request: unknown
    response: Array<Source>
  }

  /**
   * Get information about your API key.
   *
   * You can use this endpoint to get information about your API key such as
   * `requests_this_minute`, `requests_today`, and `rate_limit_model`.
   *
   * \> ℹ️ **NOTE:** If you get a 401 Unauthorized, it means your token is invalid
   * \> (malformed, non-existent, or expired).
   */
  "GET /v1/rate_limit/": {
    request: unknown
    response: OAuth2KeyInfo
  }
}

export const RoutesMeta = {
  "GET /v1/audio/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },

  "GET /v1/audio/{identifier}/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: true,
  },

  "GET /v1/audio/{identifier}/related/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: true,
  },

  "GET /v1/audio/{identifier}/thumb/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: false,
  },

  "GET /v1/audio/{identifier}/waveform/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: true,
  },

  "GET /v1/audio/stats/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },

  "POST /v1/auth_tokens/register/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },

  "POST /v1/auth_tokens/token/": {
    contentType: "application/x-www-form-urlencoded",
    pathParams: [],
    jsonResponse: true,
  },

  "GET /v1/images/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },

  "GET /v1/images/{identifier}/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: true,
  },

  "GET /v1/images/{identifier}/related/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: true,
  },

  "GET /v1/images/{identifier}/thumb/": {
    contentType: "application/json",
    pathParams: ["identifier"],
    jsonResponse: false,
  },

  "GET /v1/images/stats/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },

  "GET /v1/rate_limit/": {
    contentType: "application/json",
    pathParams: [],
    jsonResponse: true,
  },
} as const
