export interface paths {
  "/v1/audio/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Return audio files that match the query.
     *
     *     This endpoint allows you to search within specific fields, or to retrieve
     *     a collection of all audio files from a specific source, creator or tag.
     *     Results are paginated on the basis of the `page` parameter. The `page_size`
     *     parameter controls the total number of pages.
     *
     *     Although there may be millions of relevant records, only the most relevant
     *     or the most recent several thousand records can be viewed. This is by design:
     *     the search endpoint should be used to find the top 10,000 most relevant
     *     results, not for exhaustive search or bulk download of every barely relevant
     *     result. As such, the caller should not try to access pages beyond `page_count`,
     *     or else the server will reject the query.
     *
     *     ### Default search
     *     The **default search** allows users to find media based on a query string.
     *     It supports a wide range of optional filters to narrow down search results
     *     according to specific needs.
     *
     *     By default, this endpoint performs a full-text search for the value of `q` parameter.
     *     You can search within the `creator`, `title` or `tags` fields by omitting
     *     the `q` parameter and using one of these field parameters.
     *     These results can be filtered by `source`, `excluded_source`, `license`, `license_type`, `creator`, `tags`, `title`, `filter_dead`, `extension`, `mature`, `unstable__include_sensitive_results`, `category` and `length`.
     *
     *     The default search results are sorted by relevance.
     *
     *     ### Collection search
     *     The collection search allows to retrieve a collection of media from a specific source,
     *     creator or tag. The `unstable__collection` parameter is used to specify the type of collection to retrieve.
     *
     *     - `unstable__collection=tag&unstable__tag=tagName` will return the media with tag `tagName`.
     *     - `unstable__collection=source&source=sourceName` will return the media from source `sourceName`.
     *     - `unstable__collection=creator&creator=creatorName&source=sourceName` will return the media by creator `creatorName` at `sourceName`.
     *
     *     Collection results are sorted by the time they were added to Openverse, with the most recent
     *     additions appearing first. The filters such as `license` are not available for collections.
     *      */
    get: operations["audio_search"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/{identifier}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get the details of a specified audio track.
     *
     *     By using this endpoint, you can obtain info about audio files such as
     *     `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `genres`, `filesize`, `filetype`, `tags`, `alt_files`, `attribution`, `fields_matched`, `mature`, `audio_set`, `duration`, `bit_rate`, `sample_rate`, `thumbnail`, `detail_url`, `related_url`, `waveform`, `peaks` and `unstable__sensitivity` */
    get: operations["audio_detail"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/{identifier}/related/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get related audio files for a specified audio track.
     *
     *     By using this endpoint, you can get the details of related audio such as
     *     `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `genres`, `filesize`, `filetype`, `tags`, `alt_files`, `attribution`, `fields_matched`, `mature`, `audio_set`, `duration`, `bit_rate`, `sample_rate`, `thumbnail`, `detail_url`, `related_url`, `waveform`, `peaks` and `unstable__sensitivity`. */
    get: operations["audio_related"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/{identifier}/report/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /**  Report an issue about a specified audio track to Openverse.
     *
     *     By using this endpoint, you can report an audio track if it infringes
     *     copyright, contains mature or sensitive content or some other reason. */
    post: operations["audio_report"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/{identifier}/thumb/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**  Retrieve the scaled down and compressed thumbnail of the artwork of an
     *     audio track or its audio set. */
    get: operations["audio_thumb"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/{identifier}/waveform/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**  Get the waveform peaks for an audio track.
     *
     *     The peaks are provided as a list of numbers, each of these numbers being
     *     a fraction between 0 and 1. The list contains approximately 1000 numbers,
     *     although it can be slightly higher or lower, depending on the track's length. */
    get: operations["audio_waveform"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/audio/stats/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get a list of all content sources and their respective number of
     *     audio files in the Openverse catalog.
     *
     *     By using this endpoint, you can obtain info about content sources such
     *     as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`. */
    get: operations["audio_stats"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/auth_tokens/register/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /**  Register an application to access to API via OAuth2.
     *
     *     Upon registering, you will receive a `client_id` and `client_secret`,
     *     which you can then use to authenticate using the standard OAuth2 flow.
     *
     *     \> ⚠️ **WARNINGS:**
     *     \> - Store your `client_id` and `client_secret` because you will not be
     *     \>   able to retrieve them later.
     *     \> - You must keep `client_secret` confidential, as anybody with your
     *     \>   `client_secret` can impersonate your application.
     *
     *     You must verify your email address by click the link sent to you in an
     *     email. Until you do that, the application will be subject to the same
     *     rate limits as an anonymous user. */
    post: operations["register"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/auth_tokens/token/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /**  Get an access token using client credentials.
     *
     *     To authenticate your requests to the Openverse API, you need to provide
     *     an access token as a bearer token in the `Authorization` header of your
     *     requests. This endpoint takes your client ID and secret, and issues an
     *     access token.
     *
     *     \> **NOTE:** This endpoint only accepts data as
     *     \> `application/x-www-form-urlencoded`. Any other encoding will not work.
     *
     *     Once your access token expires, you can request another one from this
     *     endpoint. */
    post: operations["token"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Return images that match the query.
     *
     *     This endpoint allows you to search within specific fields, or to retrieve
     *     a collection of all images from a specific source, creator or tag.
     *     Results are paginated on the basis of the `page` parameter. The `page_size`
     *     parameter controls the total number of pages.
     *
     *     Although there may be millions of relevant records, only the most relevant
     *     or the most recent several thousand records can be viewed. This is by design:
     *     the search endpoint should be used to find the top 10,000 most relevant
     *     results, not for exhaustive search or bulk download of every barely relevant
     *     result. As such, the caller should not try to access pages beyond `page_count`,
     *     or else the server will reject the query.
     *
     *     ### Default search
     *     The **default search** allows users to find media based on a query string.
     *     It supports a wide range of optional filters to narrow down search results
     *     according to specific needs.
     *
     *     By default, this endpoint performs a full-text search for the value of `q` parameter.
     *     You can search within the `creator`, `title` or `tags` fields by omitting
     *     the `q` parameter and using one of these field parameters.
     *     These results can be filtered by `source`, `excluded_source`, `license`, `license_type`, `creator`, `tags`, `title`, `filter_dead`, `extension`, `mature`, `unstable__include_sensitive_results`, `category`, `aspect_ratio` and `size`.
     *
     *     The default search results are sorted by relevance.
     *
     *     ### Collection search
     *     The collection search allows to retrieve a collection of media from a specific source,
     *     creator or tag. The `unstable__collection` parameter is used to specify the type of collection to retrieve.
     *
     *     - `unstable__collection=tag&unstable__tag=tagName` will return the media with tag `tagName`.
     *     - `unstable__collection=source&source=sourceName` will return the media from source `sourceName`.
     *     - `unstable__collection=creator&creator=creatorName&source=sourceName` will return the media by creator `creatorName` at `sourceName`.
     *
     *     Collection results are sorted by the time they were added to Openverse, with the most recent
     *     additions appearing first. The filters such as `license` are not available for collections.
     *      */
    get: operations["images_search"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/{identifier}/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get the details of a specified image.
     *
     *     By using this endpoint, you can obtain info about images such as
     *     `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `filesize`, `filetype`, `tags`, `attribution`, `fields_matched`, `mature`, `height`, `width`, `thumbnail`, `detail_url`, `related_url` and `unstable__sensitivity` */
    get: operations["images_detail"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/{identifier}/related/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get related images for a specified image.
     *
     *     By using this endpoint, you can get the details of related images such as
     *     `id`, `title`, `indexed_on`, `foreign_landing_url`, `url`, `creator`, `creator_url`, `license`, `license_version`, `license_url`, `provider`, `source`, `category`, `filesize`, `filetype`, `tags`, `attribution`, `fields_matched`, `mature`, `height`, `width`, `thumbnail`, `detail_url`, `related_url` and `unstable__sensitivity`. */
    get: operations["images_related"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/{identifier}/report/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    get?: never
    put?: never
    /**  Report an issue about a specified image to Openverse.
     *
     *     By using this endpoint, you can report an image if it infringes
     *     copyright, contains mature or sensitive content or some other reason. */
    post: operations["images_report"]
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/{identifier}/thumb/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**  Retrieve the scaled down and compressed thumbnail of the image. */
    get: operations["images_thumb"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/{identifier}/watermark/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     * @deprecated
     *  Note that this endpoint is deprecated.
     *
     *     ---
     *
     *     🚧 **TODO:** Document this.
     */
    get: operations["images_watermark"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/oembed/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**  Retrieve the structured data for a specified image URL as per the
     *     [oEmbed spec](https://oembed.com/).
     *
     *     This info can be used to embed the image on the consumer's website. Only
     *     JSON format is supported. */
    get: operations["images_oembed"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/images/stats/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**
     *     Get a list of all content sources and their respective number of
     *     images in the Openverse catalog.
     *
     *     By using this endpoint, you can obtain info about content sources such
     *     as `source_name`, `display_name`, `source_url`, `logo_url` and `media_count`. */
    get: operations["images_stats"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
  "/v1/rate_limit/": {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    /**  Get information about your API key.
     *
     *     You can use this endpoint to get information about your API key such as
     *     `requests_this_minute`, `requests_today`, and `rate_limit_model`.
     *
     *     \> ℹ️ **NOTE:** If you get a 401 Unauthorized, it means your token is invalid
     *     \> (malformed, non-existent, or expired). */
    get: operations["key_info"]
    put?: never
    post?: never
    delete?: never
    options?: never
    head?: never
    patch?: never
    trace?: never
  }
}
export type webhooks = Record<string, never>
export interface components {
  schemas: {
    /** APIException */
    APIException: {
      /**  A description of what went wrong. */
      detail?: string
    }
    /**  A single audio file. Used in search results. */
    Audio: {
      /**  Our unique identifier for an open-licensed work. */
      id: string
      /**  The name of the media. */
      title?: string | null
      /**
       * Format: date-time
       *  The timestamp of when the media was indexed by Openverse.
       */
      indexed_on: string
      /**  The landing page of the work. */
      foreign_landing_url?: string | null
      /**  The actual URL to the media file. */
      url?: string | null
      /**  The name of the media creator. */
      creator?: string | null
      /**  A direct link to the media creator. */
      creator_url?: string | null
      /**  The name of license for the media. */
      license: string
      /**  The version of the media license. */
      license_version?: string | null
      /**  A direct link to the license deed or legal terms. */
      readonly license_url: string | null
      /**  The content provider, e.g. Flickr, Jamendo... */
      provider?: string | null
      /**  The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr. */
      source?: string | null
      /**  The top-level classification of this media file. */
      category?: string | null
      /**  An array of audio genres such as `rock`, `electronic` for `music` category, or `politics`, `sport`, `education` for `podcast` category */
      genres?: string[] | null
      /**  Number in bytes, e.g. 1024. */
      filesize?: number | null
      /**  The type of the file, related to the file extension. */
      filetype?: string | null
      /**  Tags with detailed metadata, such as accuracy. */
      tags: components["schemas"]["Tag"][] | null
      /**  JSON describing alternative files for this audio. */
      readonly alt_files: components["schemas"]["AudioAltFile"][] | null
      /**  Legally valid attribution for the media item in plain-text English. */
      readonly attribution: string | null
      /**  List the fields that matched the query for this result. */
      fields_matched: unknown[] | null
      /**  Whether the media item is marked as mature */
      mature: boolean
      /**  Reference to set of which this track is a part. */
      readonly audio_set: components["schemas"]["AudioSet"] | null
      /**  The time length of the audio file in milliseconds. */
      duration?: number | null
      /**  Number in bits per second, eg. 128000. */
      bit_rate?: number | null
      /**  Number in hertz, eg. 44100. */
      sample_rate?: number | null
      /**
       * Format: uri
       *  A direct link to the miniature artwork.
       */
      readonly thumbnail: string | null
      /**
       * Format: uri
       *  A direct link to the detail view of this audio file.
       */
      readonly detail_url: string
      /**
       * Format: uri
       *  A link to an endpoint that provides similar audio files.
       */
      readonly related_url: string
      /**
       * Format: uri
       *  A direct link to the waveform peaks.
       */
      readonly waveform: string
    }
    /**  A set of alternative files for a single audio object,
     *     rendered as a part of the `AudioSerializer` output. */
    AudioAltFile: {
      /**
       * Format: uri
       *  URL of the alternative file.
       */
      url: string
      /**  Bit rate of the alternative file. */
      bit_rate?: number
      /**  Size of the alternative file in bytes. */
      filesize?: number
      /**  File type of the alternative file. */
      filetype: string
      /**  Sample rate of the alternative file. */
      sample_rate?: number
    }
    AudioReportRequest: {
      /**
       * Format: uuid
       *  Our unique identifier for an open-licensed work.
       */
      identifier: string
      /**  The reason to report media to Openverse.
       *
       *     * `mature` - mature
       *     * `dmca` - dmca
       *     * `other` - other */
      reason: components["schemas"]["ReasonEnum"]
      /**  The explanation on why media is being reported. */
      description?: string | null
    }
    /**  An audio set, rendered as a part of the `AudioSerializer` output. */
    AudioSet: {
      /**  The name of the media. */
      title?: string | null
      /**  The landing page of the work. */
      foreign_landing_url?: string | null
      /**  The name of the media creator. */
      creator?: string | null
      /**  A direct link to the media creator. */
      creator_url?: string | null
      /**  The actual URL to the media file. */
      url?: string | null
      /**  Number in bytes, e.g. 1024. */
      filesize?: number | null
      /**  The type of the file, related to the file extension. */
      filetype?: string | null
    }
    AudioWaveform: {
      readonly len: number
      points: number[]
    }
    /** AuthenticationFailed */
    AuthenticationFailed: {
      /**  A description of what went wrong. */
      detail?: string
    }
    /**
     *  * `client_credentials` - client_credentials
     *
     */
    GrantTypeEnum: "client_credentials"
    /**  A single image. Used in search results. */
    Image: {
      /**  Our unique identifier for an open-licensed work. */
      id: string
      /**  The name of the media. */
      title?: string | null
      /**
       * Format: date-time
       *  The timestamp of when the media was indexed by Openverse.
       */
      indexed_on: string
      /**  The landing page of the work. */
      foreign_landing_url?: string | null
      /**  The actual URL to the media file. */
      url?: string | null
      /**  The name of the media creator. */
      creator?: string | null
      /**  A direct link to the media creator. */
      creator_url?: string | null
      /**  The name of license for the media. */
      license: string
      /**  The version of the media license. */
      license_version?: string | null
      /**  A direct link to the license deed or legal terms. */
      readonly license_url: string | null
      /**  The content provider, e.g. Flickr, Jamendo... */
      provider?: string | null
      /**  The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr. */
      source?: string | null
      /**  The top-level classification of this media file. */
      category?: string | null
      /**  Number in bytes, e.g. 1024. */
      filesize?: number | null
      /**  The type of the file, related to the file extension. */
      filetype?: string | null
      /**  Tags with detailed metadata, such as accuracy. */
      tags: components["schemas"]["Tag"][] | null
      /**  Legally valid attribution for the media item in plain-text English. */
      readonly attribution: string | null
      /**  List the fields that matched the query for this result. */
      fields_matched: unknown[] | null
      /**  Whether the media item is marked as mature */
      mature: boolean
      /**  The height of the image in pixels. Not always available. */
      height?: number | null
      /**  The width of the image in pixels. Not always available. */
      width?: number | null
      /**
       * Format: uri
       *  A direct link to the miniature artwork.
       */
      readonly thumbnail: string
      /**
       * Format: uri
       *  A direct link to the detail view of this audio file.
       */
      readonly detail_url: string
      /**
       * Format: uri
       *  A link to an endpoint that provides similar audio files.
       */
      readonly related_url: string
    }
    ImageReportRequest: {
      /**
       * Format: uuid
       *  Our unique identifier for an open-licensed work.
       */
      identifier: string
      /**  The reason to report media to Openverse.
       *
       *     * `mature` - mature
       *     * `dmca` - dmca
       *     * `other` - other */
      reason: components["schemas"]["ReasonEnum"]
      /**  The explanation on why media is being reported. */
      description?: string | null
    }
    /** NotAuthenticated */
    NotAuthenticated: {
      /**  A description of what went wrong. */
      detail?: string
    }
    /** NotFound */
    NotFound: {
      /**  A description of what went wrong. */
      detail?: string
    }
    OAuth2Application: {
      /**  The unique, public identifier of your application. */
      client_id: string
      /**  The secret key used to authenticate your application. */
      client_secret: string
      /**  The name of your application or project. */
      name: string
      /**  Some additional information about the application. */
      msg: string
    }
    OAuth2KeyInfo: {
      /**  The number of requests your key has performed in the last minute. */
      requests_this_minute: number | null
      /**  The number of requests your key has performed in the last day. */
      requests_today: number | null
      /**  The type of rate limit applied to your key. Can be 'standard' or 'enhanced'; enhanced users enjoy higher rate limits than their standard key counterparts. Contact Openverse if you need a higher rate limit. */
      rate_limit_model: string
      /**  Whether the application has verified the submitted email address. */
      verified: boolean
    }
    OAuth2Registration: {
      /**  A unique human-readable name for your application or project requiring access to the Openverse API. */
      name: string
      /**  A description of what you are trying to achieve with your project using the API. Please provide as much detail as possible! */
      description: string
      /**
       * Format: email
       *  A valid email that we can reach you at if we have any questions about your use case or data consumption.
       */
      email: string
    }
    /**  Serializes the response for an access token.
     *
     *     This is a dummy serializer for OpenAPI and is not actually used. */
    OAuth2Token: {
      /**  The access token that can be used to authenticate requests. */
      access_token: string
      /**  The type of token. This will always be 'Bearer'. */
      token_type: string
      /**  The number of seconds until the token expires. */
      expires_in: number
      /**  The scope of the token. */
      scope: string
    }
    /**  Serializes a request for an access token.
     *
     *     This is a dummy serializer for OpenAPI and is not actually used. */
    OAuth2TokenRequest: {
      /**  The unique, public identifier of your application. */
      client_id: string
      /**  The secret key used to authenticate your application. */
      client_secret: string
      grant_type: components["schemas"]["GrantTypeEnum"]
    }
    /**  The embedded content from a specified image URL.
     *
     *     This is essentially an `ImageSerializer` with some changes to match the oEmbed
     *     spec: https://oembed.com. */
    Oembed: {
      /**  The oEmbed version number, always set to 1.0. */
      readonly version: components["schemas"]["VersionEnum"]
      /**  The resource type, always set to 'photo' for images. */
      readonly type: components["schemas"]["TypeEnum"]
      /**  The width of the image in pixels. */
      readonly width: number
      /**  The height of the image in pixels. */
      readonly height: number
      /**  The name of the media. */
      title?: string | null
      /**  The name of the media creator. */
      author_name: string
      /**
       * Format: uri
       *  A direct link to the media creator.
       */
      author_url: string
      /**  A direct link to the license deed or legal terms. */
      readonly license_url: string | null
    }
    PaginatedAudioList: {
      /**
       *  The total number of items returned by search result.
       * @example 10000
       */
      result_count: number
      /**
       *  The total number of pages returned by search result.
       * @example 20
       */
      page_count: number
      /**
       *  The number of items per page.
       * @example 20
       */
      page_size: number
      /**
       *  The current page number returned in the response.
       * @example 1
       */
      page: number
      results: components["schemas"]["Audio"][]
      /**
       *  Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
       * @example [
       *       \{
       *         "code": "partially invalid request parameter",
       *         "message": "Some of the request parameters were bad, but we processed the request anywhere. Here's some information that might help you fix the problem for future requests."
       *       \}
       *     ]
       */
      warnings?: Record<string, never>[]
    }
    PaginatedImageList: {
      /**
       *  The total number of items returned by search result.
       * @example 10000
       */
      result_count: number
      /**
       *  The total number of pages returned by search result.
       * @example 20
       */
      page_count: number
      /**
       *  The number of items per page.
       * @example 20
       */
      page_size: number
      /**
       *  The current page number returned in the response.
       * @example 1
       */
      page: number
      results: components["schemas"]["Image"][]
      /**
       *  Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
       * @example [
       *       \{
       *         "code": "partially invalid request parameter",
       *         "message": "Some of the request parameters were bad, but we processed the request anywhere. Here's some information that might help you fix the problem for future requests."
       *       \}
       *     ]
       */
      warnings?: Record<string, never>[]
    }
    /**
     *  * `mature` - mature
     *     * `dmca` - dmca
     *     * `other` - other
     *
     */
    ReasonEnum: "mature" | "dmca" | "other"
    Source: {
      /**  The source of the media, e.g. flickr */
      source_name: string
      /**  The name of content source, e.g. Flickr */
      display_name: string
      /**
       * Format: uri
       *  The URL of the source, e.g. https://www.flickr.com
       */
      source_url: string
      /**
       * @deprecated
       *  The URL to a logo for the source.
       */
      readonly logo_url: string | null
      /**  The number of media items indexed from the source. */
      readonly media_count: number
    }
    /**  This output serializer serializes a singular tag. */
    Tag: {
      /**  The name of a detailed tag. */
      name: string
      /**
       * Format: double
       *  The accuracy of a machine-generated tag. Human-generated tags have a null accuracy field.
       */
      accuracy?: number | null
      /**
       * provider
       *  The source of the tag. When this field matches the provider for the record, the tag originated from the upstream provider. Otherwise, the tag was added with an external machine-generated labeling processes.
       */
      unstable__provider: string | null
    }
    TypeEnum: "photo"
    /** ValidationError */
    ValidationError: {
      detail?:
        | string
        | {
            [key: string]: unknown
          }
    }
    VersionEnum: "1.0"
  }
  responses: never
  parameters: never
  requestBodies: never
  headers: never
  pathItems: never
}
export type $defs = Record<string, never>
export interface operations {
  audio_search: {
    parameters: {
      query?: {
        /**  The page of results to retrieve. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth). */
        page?: number
        /**  Number of results to return per page. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth). */
        page_size?: number
        /**  A query string that should not exceed 200 characters in length */
        q?: string
        /**
         *     For default search, a comma separated list of data sources.
         *     When the `unstable__collection` parameter is used, this parameter only accepts a single source.
         *
         *     Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/audio/stats/.
         *      */
        source?: string
        /**
         *     A comma separated list of data sources to exclude from the search.
         *     Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/audio/stats/.
         *      */
        excluded_source?: string
        /**  Search by tag only. Cannot be used with `q`. The search is fuzzy, so `tags=cat` will match any value that includes the word `cat`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma. */
        tags?: string
        /**  Search by title only. Cannot be used with `q`. The search is fuzzy, so `title=photo` will match any value that includes the word `photo`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma. */
        title?: string
        /**
         *     _When `q` parameter is present, `creator` parameter is ignored._
         *
         *     **Creator collection**
         *     When used with `unstable__collection=creator&source=sourceName`, returns the collection of media
         *     by the specified creator. Notice that a single creator's media items
         *     can be found on several sources, but this collection only returns the
         *     items from the specified source.
         *     This is why for this collection, both the creator and the source
         *     parameters are required, and matched exactly. For a fuzzy creator search,
         *     use the default search without the `unstable__collection` parameter.
         *
         *     **Creator search**
         *     When used without the `unstable__collection` parameter, will search in the creator field only.
         *     The search is fuzzy, so `creator=john` will match any value that includes the
         *     word `john`. If the value contains space, items that contain any of
         *     the words in the value will match. To search for several values,
         *     join them with a comma.
         *      */
        creator?: string
        /**
         *
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *
         *     The kind of media collection to return.
         *
         *     Must be used with `unstable__tag`, `source` or `creator`+`source`
         *
         *     * `tag` - tag
         *     * `source` - source
         *     * `creator` - creator */
        unstable__collection?: "tag" | "source" | "creator"
        /**
         *
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *
         *     _Must be used with `unstable__collection=tag`_
         *
         *     Get the collection of media with a specific tag. Returns the collection of media
         *     that has the specified tag, matching exactly and entirely.
         *
         *     Differences that will cause tags to not match are:
         *     - upper and lower case letters
         *     - diacritical marks
         *     - hyphenation
         *     - spacing
         *     - multi-word tags where the query is only one of the words in the tag
         *     - multi-word tags where the words are in a different order.
         *
         *     Examples of tags that **do not** match:
         *     - "Low-Quality" and "low-quality"
         *     - "jalapeño" and "jalapeno"
         *     - "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
         *     - "dog walking" and "dog  walking" (where the latter has two spaces between the
         *     last two words, as in a typographical error)
         *     - "runner" and "marathon runner"
         *     - "exclaiming loudly" and "loudly exclaiming"
         *
         *     For non-exact or multi-tag matching, using the `tags` query parameter.
         *      */
        unstable__tag?: string
        /**  A comma separated list of licenses; available licenses include: `by`, `by-nc`, `by-nc-nd`, `by-nc-sa`, `by-nd`, `by-sa`, `cc0`, `nc-sampling+`, `pdm`, and `sampling+`. */
        license?: string
        /**  A comma separated list of license types; available license types include: `all`, `all-cc`, `commercial`, and `modification`. */
        license_type?: string
        /**  Control whether 404 links are filtered out. */
        filter_dead?: boolean
        /**  A comma separated list of desired file extensions. */
        extension?: string
        /**  Whether to include sensitive content. */
        mature?: boolean
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The field which should be the basis for sorting results.
         *
         *     * `relevance` - Relevance
         *     * `indexed_on` - Indexing date */
        unstable__sort_by?: "relevance" | "indexed_on"
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The direction of sorting. Cannot be applied when sorting by `relevance`.
         *
         *     * `desc` - Descending
         *     * `asc` - Ascending */
        unstable__sort_dir?: "desc" | "asc"
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     If enabled, the search will add a boost to results that are from authoritative sources. */
        unstable__authority?: boolean
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The boost coefficient to apply to authoritative sources, multiplied with the popularity boost. */
        unstable__authority_boost?: number
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     Whether to include results considered sensitive. */
        unstable__include_sensitive_results?: boolean
        /**  A comma separated list of categories; available categories include: `audiobook`, `music`, `news`, `podcast`, `pronunciation`, and `sound_effect`. */
        category?: string
        /**  A comma separated list of lengths; available lengths include: `long`, `medium`, `short`, and `shortest`. */
        length?: string
        /**  Whether to include the waveform peaks or not */
        peaks?: boolean
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedAudioList"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotAuthenticated"]
        }
      }
    }
  }
  audio_detail: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Audio"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  audio_related: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedAudioList"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  audio_report: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["AudioReportRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["AudioReportRequest"]
        "multipart/form-data": components["schemas"]["AudioReportRequest"]
      }
    }
    responses: {
      /**  Created */
      201: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AudioReportRequest"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
    }
  }
  audio_thumb: {
    parameters: {
      query?: {
        /**  whether to render the actual image and not a thumbnail version */
        full_size?: boolean | null
        /**  whether to compress the output image to reduce file size,defaults to opposite of `full_size` */
        compressed?: boolean | null
      }
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  Thumbnail image */
      200: {
        headers: {
          [name: string]: unknown
        }
        content?: never
      }
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  audio_waveform: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AudioWaveform"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  audio_stats: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Source"][]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
    }
  }
  register: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["OAuth2Registration"]
        "application/x-www-form-urlencoded": components["schemas"]["OAuth2Registration"]
        "multipart/form-data": components["schemas"]["OAuth2Registration"]
      }
    }
    responses: {
      /**  Created */
      201: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["OAuth2Application"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": {
            error?: string
          }
        }
      }
      /**  Too Many Requests */
      429: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIException"]
        }
      }
    }
  }
  token: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody: {
      content: {
        "application/x-www-form-urlencoded": components["schemas"]["OAuth2TokenRequest"]
      }
    }
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["OAuth2Token"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIException"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotAuthenticated"]
        }
      }
    }
  }
  images_search: {
    parameters: {
      query?: {
        /**  The page of results to retrieve. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth). */
        page?: number
        /**  Number of results to return per page. This parameter is subject to limitations based on authentication and access level. For details, refer to [the authentication documentation](#tag/auth). */
        page_size?: number
        /**  A query string that should not exceed 200 characters in length */
        q?: string
        /**
         *     For default search, a comma separated list of data sources.
         *     When the `unstable__collection` parameter is used, this parameter only accepts a single source.
         *
         *     Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/images/stats/.
         *      */
        source?: string
        /**
         *     A comma separated list of data sources to exclude from the search.
         *     Valid values are `source_name`s from the stats endpoint: https://api.openverse.org/v1/images/stats/.
         *      */
        excluded_source?: string
        /**  Search by tag only. Cannot be used with `q`. The search is fuzzy, so `tags=cat` will match any value that includes the word `cat`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma. */
        tags?: string
        /**  Search by title only. Cannot be used with `q`. The search is fuzzy, so `title=photo` will match any value that includes the word `photo`. If the value contains space, items that contain any of the words in the value will match. To search for several values, join them with a comma. */
        title?: string
        /**
         *     _When `q` parameter is present, `creator` parameter is ignored._
         *
         *     **Creator collection**
         *     When used with `unstable__collection=creator&source=sourceName`, returns the collection of media
         *     by the specified creator. Notice that a single creator's media items
         *     can be found on several sources, but this collection only returns the
         *     items from the specified source.
         *     This is why for this collection, both the creator and the source
         *     parameters are required, and matched exactly. For a fuzzy creator search,
         *     use the default search without the `unstable__collection` parameter.
         *
         *     **Creator search**
         *     When used without the `unstable__collection` parameter, will search in the creator field only.
         *     The search is fuzzy, so `creator=john` will match any value that includes the
         *     word `john`. If the value contains space, items that contain any of
         *     the words in the value will match. To search for several values,
         *     join them with a comma.
         *      */
        creator?: string
        /**
         *
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *
         *     The kind of media collection to return.
         *
         *     Must be used with `unstable__tag`, `source` or `creator`+`source`
         *
         *     * `tag` - tag
         *     * `source` - source
         *     * `creator` - creator */
        unstable__collection?: "tag" | "source" | "creator"
        /**
         *
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *
         *     _Must be used with `unstable__collection=tag`_
         *
         *     Get the collection of media with a specific tag. Returns the collection of media
         *     that has the specified tag, matching exactly and entirely.
         *
         *     Differences that will cause tags to not match are:
         *     - upper and lower case letters
         *     - diacritical marks
         *     - hyphenation
         *     - spacing
         *     - multi-word tags where the query is only one of the words in the tag
         *     - multi-word tags where the words are in a different order.
         *
         *     Examples of tags that **do not** match:
         *     - "Low-Quality" and "low-quality"
         *     - "jalapeño" and "jalapeno"
         *     - "Saint Pierre des Champs" and "Saint-Pierre-des-Champs"
         *     - "dog walking" and "dog  walking" (where the latter has two spaces between the
         *     last two words, as in a typographical error)
         *     - "runner" and "marathon runner"
         *     - "exclaiming loudly" and "loudly exclaiming"
         *
         *     For non-exact or multi-tag matching, using the `tags` query parameter.
         *      */
        unstable__tag?: string
        /**  A comma separated list of licenses; available licenses include: `by`, `by-nc`, `by-nc-nd`, `by-nc-sa`, `by-nd`, `by-sa`, `cc0`, `nc-sampling+`, `pdm`, and `sampling+`. */
        license?: string
        /**  A comma separated list of license types; available license types include: `all`, `all-cc`, `commercial`, and `modification`. */
        license_type?: string
        /**  Control whether 404 links are filtered out. */
        filter_dead?: boolean
        /**  A comma separated list of desired file extensions. */
        extension?: string
        /**  Whether to include sensitive content. */
        mature?: boolean
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The field which should be the basis for sorting results.
         *
         *     * `relevance` - Relevance
         *     * `indexed_on` - Indexing date */
        unstable__sort_by?: "relevance" | "indexed_on"
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The direction of sorting. Cannot be applied when sorting by `relevance`.
         *
         *     * `desc` - Descending
         *     * `asc` - Ascending */
        unstable__sort_dir?: "desc" | "asc"
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     If enabled, the search will add a boost to results that are from authoritative sources. */
        unstable__authority?: boolean
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     The boost coefficient to apply to authoritative sources, multiplied with the popularity boost. */
        unstable__authority_boost?: number
        /**
         *
         *
         *     _Caution: Parameters prefixed with `unstable__` are experimental and
         *     may change or be removed without notice in future updates. Use them
         *     with caution as they are not covered by our API versioning policy._
         *
         *
         *     Whether to include results considered sensitive. */
        unstable__include_sensitive_results?: boolean
        /**  A comma separated list of categories; available categories include: `digitized_artwork`, `illustration`, and `photograph`. */
        category?: string
        /**  A comma separated list of aspect ratios; available aspect ratios include: `square`, `tall`, and `wide`. */
        aspect_ratio?: string
        /**  A comma separated list of image sizes; available image sizes include: `large`, `medium`, and `small`. */
        size?: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["PaginatedImageList"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotAuthenticated"]
        }
      }
    }
  }
  images_detail: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Image"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  images_related: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Image"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  images_report: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody: {
      content: {
        "application/json": components["schemas"]["ImageReportRequest"]
        "application/x-www-form-urlencoded": components["schemas"]["ImageReportRequest"]
        "multipart/form-data": components["schemas"]["ImageReportRequest"]
      }
    }
    responses: {
      /**  Created */
      201: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ImageReportRequest"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
    }
  }
  images_thumb: {
    parameters: {
      query?: {
        /**  whether to render the actual image and not a thumbnail version */
        full_size?: boolean | null
        /**  whether to compress the output image to reduce file size,defaults to opposite of `full_size` */
        compressed?: boolean | null
      }
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  Thumbnail image */
      200: {
        headers: {
          [name: string]: unknown
        }
        content?: never
      }
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  images_watermark: {
    parameters: {
      query?: never
      header?: never
      path: {
        identifier: string
      }
      cookie?: never
    }
    requestBody?: never
    responses: {
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  images_oembed: {
    parameters: {
      query: {
        /**  The link to an image present in Openverse. */
        url: string
      }
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Oembed"]
        }
      }
      /**  Bad Request */
      400: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["ValidationError"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
      /**  Not Found */
      404: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotFound"]
        }
      }
    }
  }
  images_stats: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["Source"][]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["AuthenticationFailed"]
        }
      }
    }
  }
  key_info: {
    parameters: {
      query?: never
      header?: never
      path?: never
      cookie?: never
    }
    requestBody?: never
    responses: {
      /**  OK */
      200: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["OAuth2KeyInfo"]
        }
      }
      /**  Unauthorized */
      401: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["NotAuthenticated"]
        }
      }
      /**  Too Many Requests */
      429: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIException"]
        }
      }
      /**  Internal Server Error */
      500: {
        headers: {
          [name: string]: unknown
        }
        content: {
          "application/json": components["schemas"]["APIException"]
        }
      }
    }
  }
}
