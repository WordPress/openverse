import { createI18n } from "vue-i18n"

import { computed } from "vue"

import messages from "~~/i18n/locales/en.json"

const globalizedI18n = () => {
  const i18n = createI18n({
    locale: "en",
    fallbackLocale: "en",
    legacy: false,
    messages: {
      en: messages,
      "en-US": messages,
      ar: {},
      ru: {},
    },
  })
  return {
    ...i18n,
    t: i18n.global.t,
    localeProperties: computed(() => ({
      code: "en",
      dir: "ltr",
      nativeName: "English",
      translated: 100,
    })),
  }
}

export const i18n = globalizedI18n()

export const t = i18n.global.t
