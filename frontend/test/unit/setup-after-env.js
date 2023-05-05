import Vue from "vue"
import "@testing-library/jest-dom"
import failOnConsole from "jest-fail-on-console"

failOnConsole()

Vue.prototype.$nuxt = {
  context: {
    $sentry: {
      captureException: jest.fn(),
      captureEvent: jest.fn(),
    },
    localePath: (args) => args,
  },
}
