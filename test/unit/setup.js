import Vue from 'vue'
import VueI18n from 'vue-i18n'
import { env } from '../../nuxt.config'

// Attach nuxt config to process
for (const [key, value] of Object.entries(env)) {
  process.env[key] = value
}

Vue.use(VueI18n)

// Make sure api analytics are enabled so we can test them!
process.env.apiAnalytics = false

Vue.config.productionTip = false
Vue.config.devtools = false
