import VueI18n from 'vue-i18n'

const messages = require('~/locales/en.json')

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

export default i18n
