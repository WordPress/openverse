// This plugin is used to load any necessary client-side browser polyfills.

// Purpose: `Array.prototype.flatMap` is missing in Chrome < 69 and breaks our useStorage composable.
import "core-js/actual/array/flat-map"
import { defineNuxtPlugin } from "#imports"

export default defineNuxtPlugin(() => {})
