import Vue from "vue"
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
  emits: ["click", "mousedown"],
  methods: {
    handleClick() {
      // This is an adaptation to mimic NuxtLink's behavior,
      // see https://github.com/WordPress/openverse/pull/1118
      // We should try to remove it after migrating to Nuxt 3.
      this.$emit("mousedown")
      this.$emit("click", new MouseEvent("click"))
    },
  },
  template: '<a :href="to" v-on="$listeners" @click="handleClick"><slot /></a>',
})

config.stubs["svg-icon"] = Vue.component("SvgIcon", {
  props: ["name"],
  template: '<svg title="name" />',
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
