import Vue from "vue"
import "@testing-library/jest-dom"

Vue.prototype.$nuxt = {
  context: {
    $sentry: {
      captureException: jest.fn(),
      captureEvent: jest.fn(),
    },
  },
}
