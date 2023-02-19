# /locales/ directory

Normally when you build Openverse, you download the updated information about
locales and translation files to `src/locales` folder. To prevent too many
requests during CI, we save the locale files that are necessary to run the app
during Playwright tests.

1. `scripts/valid-locales.json` contains a list of valid locales with properties
   including their translation status (the percentage of strings that are
   translated).
2. `es.json` is the `es` locale file used for search navigation tests
   (`../playwright/e2e/search-navigation.spec.ts`).
3. `ru.json` is the `ru` locale file used for testing the translation banner
   because the current translated percentage is ~40%, which is below the banner
   threshold of 90%.
4. `ar.json` is the machine-translated `ar` locale file used for RTL testing.
