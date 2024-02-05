import Vue from "vue"

import "@testing-library/jest-dom"
import failOnConsole from "jest-fail-on-console"

import { i18n } from "~~/test/unit/test-utils/i18n"

import { normalizeFetchingError } from "~/plugins/errors"

failOnConsole()

Vue.prototype.$nuxt = {
  context: {
    $sentry: {
      captureException: jest.fn(),
      captureEvent: jest.fn(),
    },
    // i18n returned by `useI18n` composable (`useContext().i18n`)
    i18n,
    $processFetchingError: jest.fn(normalizeFetchingError),
  },
}
