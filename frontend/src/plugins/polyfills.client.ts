// This plugin is used to load any necessary client-side browser polyfills.

// Purpose: Sentry issue for issue with Chrome < 69 and our useStorage composable:
// https:openverse.sentry.io/share/issue/2b2635c85f1c4cecbe7560df5d4892b5/
import "core-js/actual/array/flat-map"
import { defineNuxtPlugin } from "#imports"

export default defineNuxtPlugin(() => {})
