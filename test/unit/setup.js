import Vue from 'vue'
import { env } from '../../nuxt.config'
import { glob } from 'glob'

// Attach nuxt config to process
for (const [key, value] of Object.entries(env)) {
  process.env[key] = value
}

// Make sure api analytics are enabled so we can test them!
process.env.disableApiAnalytics = false

// Since we're using @nuxt/components to auto-register vue components
// (which means we're not including `components: {}` in our single-file vue components)
// We need to register all components globally here!
glob('../../src/components/*', (_, matches) => {
  matches.forEach((path) => {
    const name = path.match(/(\w*)\.vue$/)[1]
    console.info({ name, path })
    Vue.component(name, require(path).default)
  })
})

Vue.config.productionTip = false
Vue.config.devtools = false
