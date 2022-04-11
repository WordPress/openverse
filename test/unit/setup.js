import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { config } from '@vue/test-utils'

import { env } from '~/utils/env'

// Attach nuxt config to process
for (const [key, value] of Object.entries(env)) {
  process.env[key] = value
}

Vue.config.productionTip = false
Vue.config.devtools = false
Vue.use(VueI18n)

config.mocks.$t = (key) => key
config.mocks.localePath = (i) => i
global.matchMedia =
  global.matchMedia ||
  function () {
    return {
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }
  }
