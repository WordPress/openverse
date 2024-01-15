import { createI18n } from "vue-i18n"

import messages from "~/locales/en.json"

const globalizedI18n = () => {
  const i18n = createI18n({
    locale: "en",
    fallbackLocale: "en",
    legacy: false,
    messages: {
      en: messages,
    },
  })
  i18n.t = i18n.global.t
  i18n.localeProperties = { code: "en", dir: "ltr" }
  return i18n
}

export const i18n = globalizedI18n()
