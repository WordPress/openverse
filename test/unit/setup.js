import Vue from 'vue'
import { env } from '../../nuxt.config'

// Attach nuxt config to process
for (const [key, value] of Object.entries(env)) {
  process.env[key] = value
}

// Make sure api analytics are enabled so we can test them!
process.env.disableApiAnalytics = false

Vue.config.productionTip = false
Vue.config.devtools = false
