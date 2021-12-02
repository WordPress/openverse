import { sendWindowMessage } from '~/utils/send-message.js'
import config from '../../nuxt.config.js'

export default {
  methods: {
    /**
     * Handles messages of type `localeSet` received by the `iframe`. Any
     * other message types will be discarded.
     *
     * @param {string} type - the nature of the message received.
     * @param {Object} value - the data sent with the message.
     * @param {string} value.locale - wpLocale code of the locale, e.g. 'en_US'.
     * @param {string} value.lang - the iso code for language
     * (and sometimes country), e.g. 'en-US'.
     * Default lang value on wp.org is 'en', and on wp.org/openverse - 'en-US'.
     * @param {'rtl'|'ltr'} [value.dir] - the locale text direction.
     */
    async localeMsgHandler({ data: { type, value } }) {
      if (type !== 'localeSet') return
      // If the locale set by wp.org is 'en_US', not 'en', this is not necessary.
      const wpLocaleValue = value.locale === 'en' ? 'en_US' : value.locale
      const locale = this.$i18n.locales.find(
        (item) => item.wpLocale === wpLocaleValue
      )
      if (locale) {
        await this.$i18n.setLocale(locale.code)
        document.documentElement.lang = locale.wpLocale.replace('_', '-')
        // Always set `dir` property, default to 'ltr'
        document.documentElement.dir = locale.dir === 'rtl' ? 'rtl' : 'ltr'
      }
    },
  },
  mounted() {
    window.addEventListener('message', this.localeMsgHandler)
    sendWindowMessage({
      debug: config.dev,
      type: 'localeGet',
      value: {},
    })
  },
  beforeDestroy() {
    window.removeEventListener('message', this.localeMsgHandler)
  },
}
