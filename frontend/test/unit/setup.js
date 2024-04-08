import Vue, { h } from "vue"
import { config } from "@vue/test-utils"

import VueI18n from "vue-i18n"

import { env } from "~/utils/env"

// Attach nuxt config to process
for (const [key, value] of Object.entries(env)) {
  process.env[key] = value
}

Vue.config.productionTip = false
Vue.config.devtools = false
Vue.use(VueI18n)

/* eslint-disable vue/one-component-per-file */
/**
 * Simplified mock of a NuxtLink component.
 */
config.stubs["nuxt-link"] = Vue.component("NuxtLink", {
  props: ["to"],
  setup(props, { slots }) {
    return () => h("a", { href: props.to }, slots.default())
  },
})

config.stubs["SvgIcon"] = Vue.component("SvgIcon", {
  props: ["name"],
  setup(props) {
    return () => h("svg", { title: props.name })
  },
})
/* eslint-enable vue/one-component-per-file */

global.matchMedia =
  global.matchMedia ||
  function () {
    return {
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    }
  }
