import VueI18n from "vue-i18n"

import { render as testingLibraryRender } from "@testing-library/vue"

import { createPinia, PiniaVuePlugin } from "~~/test/unit/test-utils/pinia"

import messages from "~/locales/en.json"

const i18n = new VueI18n({
  locale: "en",
  fallbackLocale: "en",
  messages: { en: messages },
  missingWarn: false,
  silentTranslationWarn: true,
})

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

    if (configureCb) {
      configureCb(localVue, options)
    }
  })
}

export default render
