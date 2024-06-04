## Encoding problems

In the beginning of the project, some items were saved to the database with
encoding problems. There are 3 ways that non-ASCII symbols were incorrectly
saved:

- escaped with double backslashes instead of the single backslash, e.g. `ä` ->
  `\\u00e4`
- escaped without a backslash, e.g. `ä` -> `u00e4`
- x-escaped with double backslashes, e.g. `ä` -> `\\x61`

With subsequent data re-ingestions, most titles were fixed. This problem still
exists for titles of items that were not re-ingested, and for fields that are
not simply replaced during re-ingestion, such as `tags` and
`meta_data.description`. The frontend uses a hotfix to replace these encoding
problems with the correct characters in
[title](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L73),
[tags](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L86)
and
[creator](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L124).
