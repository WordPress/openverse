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

| Name                  | Type                   | Optional? |
| --------------------- | ---------------------- | --------- |
| `attribution`         | `string`               |           |
| `category`            | `string \| null`       |           |
| `creator`             | `string`               | ✓         |
| `creator_url`         | `string`               | ✓         |
| `description`         | `string`               | ✓         |
| `detail_url`          | `string`               |           |
| `fields_matched`      | `string[]`             | ✓         |
| `filesize`            | `string`               | ✓         |
| `filetype`            | `string`               | ✓         |
| `foreign_landing_url` | `string`               |           |
| `frontendMediaType`   | _`SupportedMediaType`_ |           |
| `id`                  | `string`               |           |
| `isSensitive`         | `boolean`              |           |
| `license`             | _`License`_            |           |
| `license_url`         | `string`               | ✓         |
| `license_version`     | _`LicenseVersion`_     |           |
| `originalTitle`       | `string`               |           |
| `provider`            | `string`               |           |
| `providerName`        | `string`               | ✓         |
| `related_url`         | `string`               |           |
| `sensitivity`         | _`Sensitivity[]`_      |           |
| `source`              | `string`               | ✓         |
| `sourceName`          | `string`               | ✓         |
| `tags`                | _`Tag[]`_              |           |
| `thumbnail`           | `string`               | ✓         |
| `title`               | `string`               |           |
| `url`                 | `string`               |           |

### id

the UUID4 identifier of the media item

**See also:**

- [UUID4](<https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_(random)>)

### originalTitle

the raw name of the creative work, as returned by the API

### title

the name of the creative work; This involves the following kinds of changes to
the original title:

- remove the file extension
- escape HTML
- handle empty titles

## Interface `ImageDetail`

| Name                | Type      | Optional? |
| ------------------- | --------- | --------- |
| `frontendMediaType` | `"image"` |           |
| `height`            | `number`  | ✓         |
| `width`             | `number`  | ✓         |

### height

the vertical length of the image in pixels

### width

the horizontal length of the image in pixels

## Interface `AudioDetail`

| Name                | Type                                       | Optional? |
| ------------------- | ------------------------------------------ | --------- |
| `alt_files`         | `{ provider: string; filetype: string }[]` | ✓         |
| `audio_set`         | _`AudioSet`_                               | ✓         |
| `bit_rate`          | `number`                                   | ✓         |
| `duration`          | `number`                                   | ✓         |
| `frontendMediaType` | `"audio"`                                  |           |
| `genres`            | `string[]`                                 | ✓         |
| `hasLoaded`         | `boolean`                                  | ✓         |
| `length`            | `string`                                   | ✓         |
| `peaks`             | `number[]`                                 | ✓         |
| `sample_rate`       | `number`                                   | ✓         |
| `waveform`          | `string`                                   | ✓         |

### bit_rate

amount of digital audio data transmitted or processed in unit time; This field
holds numbers measured in bits per second.

**See also:**

- [Wikipedia](https://en.wikipedia.org/wiki/Bit_rate#Audio)

### duration

the time period of the track in milliseconds

### sample_rate

number of samples for digital representation taken in unit time; This field
holds numbers measured in hertz.

**See also:**

- [Wikipedia](<https://en.wikipedia.org/wiki/Sampling_(signal_processing)#Audio_sampling>)
