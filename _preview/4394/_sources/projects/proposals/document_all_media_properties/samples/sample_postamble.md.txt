# sample_postamble.md

## Additional Notes

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
