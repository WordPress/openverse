import VueI18n from "vue-i18n"

const messages = require("~/locales/en.json")

const i18n = new VueI18n({
  locale: "en",
  fallbackLocale: "en",
  messages: {
    en: messages,
  },
})
i18n.localeProperties = { code: "en", dir: "ltr" }
export { i18n }
