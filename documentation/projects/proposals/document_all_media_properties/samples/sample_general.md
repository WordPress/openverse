[//]: # "Preamble"

# Openverse Media Properties

_This document is auto-generated from the source code in
`utilities/media_props_gen/media_props_generation.py`. _

This is a list of the media properties, with the descriptions of corresponding
database columns and Python objects that are used to store and retrieve media
data. The order of the properties corresponds to their order in the `image_view`
materialized view.

[//]: # "Postamble"

## Additional Notes (Postamble)

### Common issues

#### Incorrectly escaped Unicode characters

In: `title`, `tags`, `creator` Sometimes, Unicode characters were encoded
incorrectly. Symbols like `\u<xxxx>` were saved as either `\\u<xxxx>` or
`u<xxxx>`. Thus, instead of showing the non-ascii symbols, they are shown as
gibberish in the UI. This is addressed in the Nuxt front end. When data refresh
is run, the incorrect values can be replaced if the `upsert_strategy` for the
column is `newest_non_null`. However, for the strategies that update the value
instead of replacing it, this results in duplication of the values. Thus, some
items have duplicated tags: the correctly-encoded tags cannot replace the
incorrectly-encoded tags because they are different.
