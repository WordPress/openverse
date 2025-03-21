# sample_media_properties.md

## Title

The title of the work. If blank, uses "This work" for the attribution sentence
(This work by creator is licensed with CC BY). Shape of the data and Selection
criteria

We select the default title returned by the provider. It can be blank. Blank
values (whether None or empty string "") are saved as empty string in the
database (TODO: check if this is true). Existing data problems

Some media items had incorrectly encoded titles [^1 - Link to a description of
Unicode encoding problem in the "postamble"]. This is compensated for in the
Frontend (link to the code that fixes title encoding). This problem has been
fixed for the items that have been reingested after some time in 2020, but might
still persist for items that were not updated since then. Link to issues for
fixing the encoding in the catalog/api/frontend. Some Wikimedia titles have a
shape of "FILE:xxx.svg". The provider script removes them now, but this is still
a problem for items that were ingested earlier. The "FILE" and ".extension" are
removed in the frontend (link to the code). Link to the issue to fix it in the
API.

## `identifier`

Used for `image` and `audio` Openverse `identifier` is generated during the
ingestion process when the image is inserted into the `image` table for the
first time.

## `tags`

### Media Type

Used for `image` and `audio`

### Name in provider scripts and `add_item`

`raw_tags`

### Description

The list of short descriptive labels or keywords for the media item.

### Shape of the data collected by provider scripts

Provider scripts collect tags as a list of strings.

Provider API scripts collect the following items as tags: `finnish_museums`
(`subjects`), `flickr` (tags, discards tags that are longer than max_length and
sorts them for consistency), `inaturalist`(taxons),
`metropolitan_museum`(department, medium, culture, objectName, artist name,
classification, object date, credit line, period, tags), `nappy` (tags), `nypl`
(tags are inside meta_data), `rawpixel` (popular_keywords excluding the license
names - should remove this to rely on MediaStore?), `smithsonian`
(indexedStructured), `stocksnap` (keywords), `wordpress` (photo_tag).

#TODO: Fix `nypl` tags collection

#TODO: Remove `rawpixel` tag filtering

### Data transformation in `MediaStore`

The `MediaStore` converts each tag into a dictionary with `name` and `provider`
properties. For example, ["tag1"] becomes
`{ "name": "tag1", "provider": "provider1"}`.

### Data transformation in `ingestion_server`/`api`

Some redundant tags (such as `uploaded_by` or the tags with licenses) are
filtered out in the `MediaStore`. Some images also have AI-generated tags from
`clarifai` and `Recognition`. These tags contain the label of what is in the
image, with the accuracy of detection
(`{ "name": "cat", "accuracy": 0.95, "provider": "clarifai"}`). It was
previously determined that tags with an accuracy score below 0.90 are often
unreliable, so those tags are discarded during the
[data cleanup process](https://github.com/WordPress/openverse/blob/a281dc472fbca281bfaa623ebe5ec0b0feab31ee/ingestion_server/ingestion_server/cleanup.py#L114)
in the `ingestion_server`.

### Data inconsistencies in the database

Some tags collected in the beginning had incorrectly escaped Unicode characters.
When the items were updated during data refresh, both the correct and incorrect
tags were saved because they were different. This is mitigated in
[Nuxt](https://github.com/WordPress/openverse/blob/a281dc472fbca281bfaa623ebe5ec0b0feab31ee/frontend/src/utils/decode-media-data.ts#L95).
