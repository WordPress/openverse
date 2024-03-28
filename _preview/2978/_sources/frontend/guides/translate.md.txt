# Translate

## Fallbacks

If the translation for a string is missing, the list of fallback languages will
be checked, in order, for a translation. If one is found, it will be used. If
none is found, the final fallback, which is English will be used to render the
text.

For example, _Español de México_ / Spanish (Mexico) falls back to _Español_ /
Spanish (Spain) as the latter has a higher translation coverage.

If you know that a particular language is compatible with another with higher
translation coverage, you can modify the fallback chain defined in the
`frontend/src/locales/scripts/locale-fallback.json` file, and submit a PR.

Going back to the same example, it would be defined in the fallback file as
follows.

```json
{
  "es-mx": ["es"]
}
```

English is the final fallback for all languages as it always has 100% coverage.
You need not define it explicitly as it's specified as the default.

```json
{
  "default": ["en"]
}
```
