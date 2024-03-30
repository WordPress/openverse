# API Media Properties

_This document is auto-generated from the source code in
[/api/api/management/commands/documentmedia.py](https://github.com/WordPress/openverse/blob/main/api/api/management/commands/documentmedia.py)._

This is a list of the media properties, with the descriptions of corresponding
database columns and Python objects that are used to store and retrieve media
data.

## General notes

The columns are sorted alphabetically and separated into relations (used to
establish relationships to other models) and values (used to hold some data
value). Note that relation fields are always nullable.

## Audio

| Name              | Type              | DB type | Nature       | To               |
| ----------------- | ----------------- | ------- | ------------ | ---------------- |
| `audio_report`    | `ForeignKey`      | `uuid`  | One To Many  | `AudioReport`    |
| `audioset`        | `ForeignObject`   |         | Many To One  | `AudioSet`       |
| `deleted_audio`   | `OneToOneField`   | `uuid`  | One To One   | `DeletedAudio`   |
| `lists`           | `ManyToManyField` |         | Many To Many | `AudioList`      |
| `sensitive_audio` | `OneToOneField`   | `uuid`  | One To One   | `SensitiveAudio` |

| Name                           | Type            | DB type                    | Constraints                   | Default |
| ------------------------------ | --------------- | -------------------------- | ----------------------------- | ------- |
| `alt_files`                    | `JSONField`     | `jsonb`                    |                               |         |
| `audio_set_foreign_identifier` | `CharField`     | `varchar(1000)`            |                               |         |
| `audio_set_position`           | `IntegerField`  | `integer`                  |                               |         |
| `bit_rate`                     | `IntegerField`  | `integer`                  |                               |         |
| `category`                     | `CharField`     | `varchar(80)`              |                               |         |
| `created_on`                   | `DateTimeField` | `timestamp with time zone` | not null                      |         |
| `creator`                      | `CharField`     | `varchar(2000)`            |                               |         |
| `creator_url`                  | `CharField`     | `varchar(2000)`            |                               |         |
| `duration`                     | `IntegerField`  | `integer`                  |                               |         |
| `filesize`                     | `IntegerField`  | `integer`                  |                               |         |
| `filetype`                     | `CharField`     | `varchar(80)`              |                               |         |
| `foreign_identifier`           | `CharField`     | `varchar(1000)`            |                               |         |
| `foreign_landing_url`          | `CharField`     | `varchar(1000)`            |                               |         |
| `genres`                       | `CharField[]`   | `varchar(80)[]`            | not blank                     |         |
| `id`                           | `AutoField`     | `integer`                  | not null; unique; primary key |         |
| `identifier`                   | `UUIDField`     | `uuid`                     | not null; not blank; unique   |         |
| `last_synced_with_source`      | `DateTimeField` | `timestamp with time zone` |                               |         |
| `license`                      | `CharField`     | `varchar(50)`              | not null; not blank           |         |
| `license_version`              | `CharField`     | `varchar(25)`              |                               |         |
| `meta_data`                    | `JSONField`     | `jsonb`                    |                               |         |
| `provider`                     | `CharField`     | `varchar(80)`              |                               |         |
| `removed_from_source`          | `BooleanField`  | `boolean`                  | not null; not blank           | `False` |
| `sample_rate`                  | `IntegerField`  | `integer`                  |                               |         |
| `source`                       | `CharField`     | `varchar(80)`              |                               |         |
| `tags`                         | `JSONField`     | `jsonb`                    |                               |         |
| `thumbnail`                    | `CharField`     | `varchar(1000)`            |                               |         |
| `title`                        | `CharField`     | `varchar(2000)`            |                               |         |
| `updated_on`                   | `DateTimeField` | `timestamp with time zone` | not null                      |         |
| `url`                          | `CharField`     | `varchar(1000)`            | unique                        |         |
| `view_count`                   | `IntegerField`  | `integer`                  |                               | `0`     |
| `watermarked`                  | `BooleanField`  | `boolean`                  |                               |         |

### `alt_files`

**Help text:** JSON describing alternative files for this audio.

### `audio_set_foreign_identifier`

**Help text:** Reference to set of which this track is a part.

### `audio_set_position`

**Help text:** Ordering of the audio in the set.

### `audioset`

This is a virtual foreign-key to `AudioSet` built on top of the fields
`audio_set_foreign_identifier` and `provider`.

### `bit_rate`

**Help text:** Number in bits per second, eg. 128000.

### `category`

**Help text:** The top-level classification of this media file.

### `creator`

**Help text:** The name of the media creator.

### `creator_url`

**Help text:** A direct link to the media creator.

### `duration`

**Help text:** The time length of the audio file in milliseconds.

### `filesize`

**Help text:** Number in bytes, e.g. 1024.

### `filetype`

**Help text:** The type of the file, related to the file extension.

### `foreign_identifier`

**Help text:** The identifier provided by the upstream source.

### `foreign_landing_url`

**Help text:** The landing page of the work.

### `genres`

**Help text:** An array of audio genres such as `rock`, `electronic` for `music`
category, or `politics`, `sport`, `education` for `podcast` category

### `id`

This is Django's automatic primary key, used for models that do not define one
explicitly.

### `identifier`

**Help text:** Our unique identifier for an open-licensed work.

### `license`

**Help text:** The name of license for the media.

### `license_version`

**Help text:** The version of the media license.

### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

### `sample_rate`

**Help text:** Number in hertz, eg. 44100.

### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

### `tags`

**Help text:** Tags with detailed metadata, such as accuracy.

### `thumbnail`

**Help text:** The thumbnail for the media.

### `title`

**Help text:** The name of the media.

### `url`

**Help text:** The actual URL to the media file.

## Image

| Name              | Type              | DB type | Nature       | To               |
| ----------------- | ----------------- | ------- | ------------ | ---------------- |
| `deleted_image`   | `OneToOneField`   | `uuid`  | One To One   | `DeletedImage`   |
| `image_report`    | `ForeignKey`      | `uuid`  | One To Many  | `ImageReport`    |
| `lists`           | `ManyToManyField` |         | Many To Many | `ImageList`      |
| `sensitive_image` | `OneToOneField`   | `uuid`  | One To One   | `SensitiveImage` |

| Name                      | Type            | DB type                    | Constraints                   | Default |
| ------------------------- | --------------- | -------------------------- | ----------------------------- | ------- |
| `category`                | `CharField`     | `varchar(80)`              |                               |         |
| `created_on`              | `DateTimeField` | `timestamp with time zone` | not null                      |         |
| `creator`                 | `CharField`     | `varchar(2000)`            |                               |         |
| `creator_url`             | `CharField`     | `varchar(2000)`            |                               |         |
| `filesize`                | `IntegerField`  | `integer`                  |                               |         |
| `filetype`                | `CharField`     | `varchar(80)`              |                               |         |
| `foreign_identifier`      | `CharField`     | `varchar(1000)`            |                               |         |
| `foreign_landing_url`     | `CharField`     | `varchar(1000)`            |                               |         |
| `height`                  | `IntegerField`  | `integer`                  |                               |         |
| `id`                      | `AutoField`     | `integer`                  | not null; unique; primary key |         |
| `identifier`              | `UUIDField`     | `uuid`                     | not null; not blank; unique   |         |
| `last_synced_with_source` | `DateTimeField` | `timestamp with time zone` |                               |         |
| `license`                 | `CharField`     | `varchar(50)`              | not null; not blank           |         |
| `license_version`         | `CharField`     | `varchar(25)`              |                               |         |
| `meta_data`               | `JSONField`     | `jsonb`                    |                               |         |
| `provider`                | `CharField`     | `varchar(80)`              |                               |         |
| `removed_from_source`     | `BooleanField`  | `boolean`                  | not null; not blank           | `False` |
| `source`                  | `CharField`     | `varchar(80)`              |                               |         |
| `tags`                    | `JSONField`     | `jsonb`                    |                               |         |
| `thumbnail`               | `CharField`     | `varchar(1000)`            |                               |         |
| `title`                   | `CharField`     | `varchar(2000)`            |                               |         |
| `updated_on`              | `DateTimeField` | `timestamp with time zone` | not null                      |         |
| `url`                     | `CharField`     | `varchar(1000)`            | unique                        |         |
| `view_count`              | `IntegerField`  | `integer`                  |                               | `0`     |
| `watermarked`             | `BooleanField`  | `boolean`                  |                               |         |
| `width`                   | `IntegerField`  | `integer`                  |                               |         |

### `category`

**Help text:** The top-level classification of this media file.

### `creator`

**Help text:** The name of the media creator.

### `creator_url`

**Help text:** A direct link to the media creator.

### `filesize`

**Help text:** Number in bytes, e.g. 1024.

### `filetype`

**Help text:** The type of the file, related to the file extension.

### `foreign_identifier`

**Help text:** The identifier provided by the upstream source.

### `foreign_landing_url`

**Help text:** The landing page of the work.

### `height`

**Help text:** The height of the image in pixels. Not always available.

### `id`

This is Django's automatic primary key, used for models that do not define one
explicitly.

### `identifier`

**Help text:** Our unique identifier for an open-licensed work.

### `license`

**Help text:** The name of license for the media.

### `license_version`

**Help text:** The version of the media license.

### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

### `tags`

**Help text:** Tags with detailed metadata, such as accuracy.

### `thumbnail`

**Help text:** The thumbnail for the media.

### `title`

**Help text:** The name of the media.

### `url`

**Help text:** The actual URL to the media file.

### `width`

**Help text:** The width of the image in pixels. Not always available.
