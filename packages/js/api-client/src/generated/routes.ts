/* eslint-disable eslint-comments/no-unlimited-disable */
/* eslint-disable */

/**
 * This file is generated from a template. Do not edit it by hand!
 *
 * @see {@link https://docs.openverse.org/packages/js/api-client/index.html#development-and-implementation-details}
 */

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

export type Routes = {
  /**
   *
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
   *
   */
  "GET /v1/audio/": {
    request: {
      params?: {
        page?: number
        page_size?: number
        q?: string
        source?: string
        excluded_source?: string
        tags?: string
        title?: string
        creator?: string
        unstable__collection?: "tag" | "source" | "creator"
        unstable__tag?: string
        license?: string
        license_type?: string
        filter_dead?: boolean
        extension?: string
        mature?: boolean
        unstable__sort_by?: "relevance" | "indexed_on"
        unstable__sort_dir?: "desc" | "asc"
        unstable__authority?: boolean
        unstable__authority_boost?: number
        unstable__include_sensitive_results?: boolean
        category?: string
        length?: string
        peaks?: boolean
      }
    }
    response: PaginatedAudioList
  }

  /**
   *
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
   *
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
        full_size?: boolean
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
   *
   * Get a list of all content sources and their respective number of
   * audio files in the Openverse catalog.
   *
   * By using this endpoint, you can obtain info about content sources such
   * as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`.
   */
  "GET /v1/audio/stats/": {
    request: {}
    response: Array<Source>
  }

  /**
   * Register an application to access to API via OAuth2.
   *
   * Upon registering, you will receive a `client_id` and `client_secret`,
   * which you can then use to authenticate using the standard OAuth2 flow.
   *
   * > ⚠️ **WARNINGS:**
   * > - Store your `client_id` and `client_secret` because you will not be
   * >   able to retrieve them later.
   * > - You must keep `client_secret` confidential, as anybody with your
   * >   `client_secret` can impersonate your application.
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
   * > **NOTE:** This endpoint only accepts data as
   * > `application/x-www-form-urlencoded`. Any other encoding will not work.
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
   *
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
   *
   */
  "GET /v1/images/": {
    request: {
      params?: {
        page?: number
        page_size?: number
        q?: string
        source?: string
        excluded_source?: string
        tags?: string
        title?: string
        creator?: string
        unstable__collection?: "tag" | "source" | "creator"
        unstable__tag?: string
        license?: string
        license_type?: string
        filter_dead?: boolean
        extension?: string
        mature?: boolean
        unstable__sort_by?: "relevance" | "indexed_on"
        unstable__sort_dir?: "desc" | "asc"
        unstable__authority?: boolean
        unstable__authority_boost?: number
        unstable__include_sensitive_results?: boolean
        category?: string
        aspect_ratio?: string
        size?: string
      }
    }
    response: PaginatedImageList
  }

  /**
   *
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
   *
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
        full_size?: boolean
        compressed?: boolean
      }
    }
    response: ReadableStream
  }

  /**
   *
   * Get a list of all content sources and their respective number of
   * images in the Openverse catalog.
   *
   * By using this endpoint, you can obtain info about content sources such
   * as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`.
   */
  "GET /v1/images/stats/": {
    request: {}
    response: Array<Source>
  }

  /**
   * Get information about your API key.
   *
   * You can use this endpoint to get information about your API key such as
   * `requests_this_minute`, `requests_today`, and `rate_limit_model`.
   *
   * > ℹ️ **NOTE:** If you get a 401 Unauthorized, it means your token is invalid
   * > (malformed, non-existent, or expired).
   */
  "GET /v1/rate_limit/": {
    request: {}
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
/* eslint-enable */
