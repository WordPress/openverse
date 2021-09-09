import { sendWindowMessage } from '~/utils/send-message.js'
import config from '../../nuxt.config.js'

export default {
  data() {
    return {
      /**
       * Handles messages of type `localeSet` received by the `iframe`. Any
       * other message types will by discarded.
       *
       * @param {string} type - the nature of the message received
       * @param {{ locale: string, lang: string }} value - the data sent with the message
       */
      localeMsgHandler: ({ data: { type, value } }) => {
        if (type !== 'localeSet') return

        const locale = this.$i18n.locales.find(
          (item) => item.wpLocale === value.locale
        )
        if (locale) {
          this.$i18n.setLocale(locale.code)
          document.documentElement.lang = value.lang
        }
      },
    }
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
