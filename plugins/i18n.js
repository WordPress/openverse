// See: https://nuxtjs.org/guides/directory-structure/plugins
import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

function loadLocaleMessages() {
  const locales = require.context(
    '../src/locales',
    true,
    /[A-Za-z0-9-_,\s]+\.json$/i
  )
  const messages = {}
  locales.keys().forEach((key) => {
    const matched = key.match(/([A-Za-z0-9-_]+)\./i)
    if (matched && matched.length > 1) {
      const locale = matched[1]
      messages[locale] = locales(key)
    }
  })
  return messages
}

export default ({ app }) => {
  // Set i18n instance on app
  // This way we can use it in middleware and pages asyncData/fetch
  // eslint-disable-next-line no-param-reassign
  app.i18n = new VueI18n({
    locale:
      typeof window !== 'undefined'
        ? window.localStorage.getItem('locale') || 'en'
        : 'en',
    fallbackLocale: 'en',
    messages: loadLocaleMessages(),
  })
}
