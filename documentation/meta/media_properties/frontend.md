# Frontend Media Properties

_This document is auto-generated from the source code in
[/frontend/scripts/document-media.js](https://github.com/WordPress/openverse/blob/main/frontend/scripts/document-media.js)._

This is a list of the media properties, with the descriptions of corresponding
TypeScript types that are used in the frontend to hold media objects.

## General notes

The columns are sorted alphabetically. Both interfaces `ImageDetail` and
`AudioDetail` inherit from interface `Media` so the tables for those interfaces
only show their additional fields.

Some types in the "Type" column may refer to interfaces or types defined in the
frontend codebase. In such cases it is advised to refer to the source file
[/frontend/src/types/media.ts](https://github.com/WordPress/openverse/blob/main/frontend/src/types/media.ts)
and trace the source of the type definitions. Such types are italicised for
clarity.

## Interface `Media`

### Fields

| Name                                                      | Type                          | Optional? |
| --------------------------------------------------------- | ----------------------------- | --------- |
| [`attribution`](#Media-attribution-notes)                 | `string`                      |           |
| [`category`](#Media-category-notes)                       | `string \| null`              | ✓         |
| [`creator`](#Media-creator-notes)                         | `string`                      | ✓         |
| [`creator_url`](#Media-creator_url-notes)                 | `string`                      | ✓         |
| [`description`](#Media-description-notes)                 | `string`                      | ✓         |
| [`detail_url`](#Media-detail_url-notes)                   | `string`                      |           |
| [`fields_matched`](#Media-fields_matched-notes)           | `string[]`                    | ✓         |
| [`filesize`](#Media-filesize-notes)                       | `string`                      | ✓         |
| [`filetype`](#Media-filetype-notes)                       | `string`                      | ✓         |
| [`foreign_landing_url`](#Media-foreign_landing_url-notes) | `string`                      |           |
| `frontendMediaType`                                       | `SupportedMediaType` (custom) |           |
| [`id`](#Media-id-notes)                                   | `string`                      |           |
| [`isSensitive`](#Media-isSensitive-notes)                 | `boolean`                     |           |
| [`license`](#Media-license-notes)                         | `License` (custom)            |           |
| [`license_url`](#Media-license_url-notes)                 | `string`                      | ✓         |
| [`license_version`](#Media-license_version-notes)         | `LicenseVersion` (custom)     |           |
| [`originalTitle`](#Media-originalTitle-notes)             | `string`                      |           |
| [`provider`](#Media-provider-notes)                       | `string`                      |           |
| [`providerName`](#Media-providerName-notes)               | `string`                      |           |
| [`related_url`](#Media-related_url-notes)                 | `string`                      |           |
| [`sensitivity`](#Media-sensitivity-notes)                 | `Sensitivity[]` (custom)      |           |
| [`source`](#Media-source-notes)                           | `string`                      |           |
| [`sourceName`](#Media-sourceName-notes)                   | `string`                      |           |
| [`tags`](#Media-tags-notes)                               | `Tag[]` (custom)              |           |
| [`thumbnail`](#Media-thumbnail-notes)                     | `string`                      | ✓         |
| [`title`](#Media-title-notes)                             | `string`                      |           |
| [`url`](#Media-url-notes)                                 | `string`                      |           |

### Notes

(Media-attribution-notes)=

#### `attribution`

The full text to properly attribute the work to the creator.

(Media-category-notes)=

#### `category`

The descriptive category describing the work.

(Media-creator-notes)=

#### `creator`

The text name, handle, or username of the author of the creative work.

(Media-creator_url-notes)=

#### `creator_url`

A URL to the creator's profile on the provider or other personal webpage,
depending on the provider.

(Media-description-notes)=

#### `description`

A long test describing the media, from the provider.

(Media-detail_url-notes)=

#### `detail_url`

The API url of the detail view of a media.

(Media-fields_matched-notes)=

#### `fields_matched`

An array of field names that matched the search query.

(Media-filesize-notes)=

#### `filesize`

A number representing the size of the media in bytes.

(Media-filetype-notes)=

#### `filetype`

A string representing the filetype of the media. Please note this is not an
exact representation of extension or MIME type.

(Media-foreign_landing_url-notes)=

#### `foreign_landing_url`

A URL to the page where the media item is hosted on the foreign provider's site.
This is often used to give credit to the original source or for users to find
more information.

(Media-id-notes)=

#### `id`

the UUID4 identifier of the media item

**See also:**

- [UUID4](<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>)

(Media-isSensitive-notes)=

#### `isSensitive`

Indicates if the media is marked as sensitive. If true, the media has
sensitivity markers that might require user discretion or warnings.

(Media-license-notes)=

#### `license`

The code of the open copy-left license assigned to the work.

(Media-license_url-notes)=

#### `license_url`

A link to the landing page of the License, typically the deed or another
informational page.

(Media-license_version-notes)=

#### `license_version`

The version number of the Creative Commons license as a string, or an empty
string.

(Media-originalTitle-notes)=

#### `originalTitle`

The raw name of the creative work, as returned by the API.

(Media-provider-notes)=

#### `provider`

A snake_cased slug representing the media's provider. Corresponds to the
`source_name` field of provider results from the API's `/stats/` endpoints.

(Media-providerName-notes)=

#### `providerName`

A presentational string (with capitalization, spaces, punctuation, and so on),
representing the media's provider. Corresponds to the `display_name` field of
provider results from the API's `/stats/` endpoints.

(Media-related_url-notes)=

#### `related_url`

The API URL which provides a list of related media results.

(Media-sensitivity-notes)=

#### `sensitivity`

An array of sensitivity markers. These markers indicate various sensitivity or
content warning categories applicable to the media.

(Media-source-notes)=

#### `source`

A snake_cased slug representing the media's source. Corresponds to the
`source_name` field of provider results from the API's `/stats/` endpoints.

(Media-sourceName-notes)=

#### `sourceName`

A presentational string (with capitalization, spaces, punctuation, and so on),
representing the media's source. Corresponds to the `display_name` field of
provider results from the API's `/stats/` endpoints.

(Media-tags-notes)=

#### `tags`

An array of tags, used to query the media or present on the frontend to find
related media.

(Media-thumbnail-notes)=

#### `thumbnail`

A URL to a thumbnail image of the media. Typically album art for an audio track,
or a minified thumbnail for image works.

(Media-title-notes)=

#### `title`

the name of the creative work; This involves the following kinds of changes to
the original title:

- remove the file extension
- escape HTML
- handle empty titles

(Media-url-notes)=

#### `url`

A URL pointing to the actual media file on the provider.

## Interface `ImageDetail`

### Fields

| Name                                  | Type                | Optional? |
| ------------------------------------- | ------------------- | --------- |
| `frontendMediaType`                   | `"image"` (literal) |           |
| [`height`](#ImageDetail-height-notes) | `number`            | ✓         |
| [`width`](#ImageDetail-width-notes)   | `number`            | ✓         |

### Notes

(ImageDetail-height-notes)=

#### `height`

The vertical length of the image, in pixels.

(ImageDetail-width-notes)=

#### `width`

The horizontal length of the image, in pixels.

## Interface `AudioDetail`

### Fields

| Name                                            | Type                                       | Optional? |
| ----------------------------------------------- | ------------------------------------------ | --------- |
| [`alt_files`](#AudioDetail-alt_files-notes)     | `{ provider: string; filetype: string }[]` | ✓         |
| [`audio_set`](#AudioDetail-audio_set-notes)     | `AudioSet` (custom)                        | ✓         |
| [`bit_rate`](#AudioDetail-bit_rate-notes)       | `number`                                   | ✓         |
| [`duration`](#AudioDetail-duration-notes)       | `number`                                   | ✓         |
| `frontendMediaType`                             | `"audio"` (literal)                        |           |
| [`genres`](#AudioDetail-genres-notes)           | `string[]`                                 | ✓         |
| [`hasLoaded`](#AudioDetail-hasLoaded-notes)     | `boolean`                                  | ✓         |
| [`peaks`](#AudioDetail-peaks-notes)             | `number[]`                                 | ✓         |
| [`sample_rate`](#AudioDetail-sample_rate-notes) | `number`                                   | ✓         |
| [`waveform`](#AudioDetail-waveform-notes)       | `string`                                   | ✓         |

### Notes

(AudioDetail-alt_files-notes)=

#### `alt_files`

An array of alternative files of different filetypes. This can include different
formats of the audio track for compatibility and quality options.

(AudioDetail-audio_set-notes)=

#### `audio_set`

An object representing a group of audio tracks this track belongs to, like an
album or podcast.

(AudioDetail-bit_rate-notes)=

#### `bit_rate`

Amount of digital audio data transmitted or processed in unit time. This field
holds numbers measured in bits per second (bps).

**See also:**

- [Wikipedia](https://en.wikipedia.org/wiki/Bit_rate#Audio)

(AudioDetail-duration-notes)=

#### `duration`

The duration of the track in milliseconds.

(AudioDetail-genres-notes)=

#### `genres`

A raw list of strings representing musical genres.

(AudioDetail-hasLoaded-notes)=

#### `hasLoaded`

Set and managed by the frontend client-side to indicate if the audio has been
fully loaded. Useful for managing UI elements based on the loading state of the
audio.

(AudioDetail-peaks-notes)=

#### `peaks`

An array of peak amplitude values used to generate a visual representation of
the audio waveform.

(AudioDetail-sample_rate-notes)=

#### `sample_rate`

Number of samples for digital representation taken in unit time. This field
holds numbers measured in hertz (Hz).

**See also:**

- [Wikipedia](<https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Audio_sampling>)

(AudioDetail-waveform-notes)=

#### `waveform`

The URL of the API `/wavepoint` endpoint for the audio track. This endpoint
provides the full peaks array for the track.
