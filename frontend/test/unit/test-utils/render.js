import VueI18n from "vue-i18n"

import { render as testingLibraryRender } from "@testing-library/vue"

import { createPinia, PiniaVuePlugin } from "~~/test/unit/test-utils/pinia"
import { i18n } from "~~/test/unit/test-utils/i18n"

/**
 * @returns {ReturnType<typeof testingLibraryRender>}
 */
export const render = (Component, options = {}, configureCb = null) => {
  if (!options?.i18n) {
    options.i18n = i18n
  }
  if (!options?.pinia) {
    options.pinia = createPinia()
  }

  return testingLibraryRender(Component, options, (localVue) => {
    localVue.use(VueI18n)
    localVue.use(PiniaVuePlugin)

    // This callback can be used to set up the store
    if (configureCb) {
      configureCb(localVue, options)
    }
  })
}
