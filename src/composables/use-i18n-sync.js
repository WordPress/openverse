import { sendWindowMessage } from '~/utils/send-message.js'
import config from '../../nuxt.config.js'
import untranslatedLocales from '../locales/scripts/untranslated-locales.json'
import {
  computed,
  onMounted,
  onUnmounted,
  reactive,
  ref,
  useContext,
} from '@nuxtjs/composition-api'
import { StorageSerializers, useStorage } from '~/composables/use-storage'

const BASE_URL = 'https://translate.wordpress.org/projects/meta/openverse/'

export default function useI18nSync() {
  const { i18n } = useContext()

  const currentLocale = computed(() => {
    return i18n.locales.find((item) => item.code === i18n.locale)
  })
  const showBanner = ref(false)
  const bannerLocale = reactive({
    code: i18n.locale,
    name: currentLocale.value.name,
  })

  /**
   * Updates the i18n locale code and sets the html lang and dir attributes.
   *
   * @param {Object} [locale]
   * @param {string} locale.code - the locale code as used in i18n.
   * @param {string} locale.lang - value of the HTML lang property.
   * @param {'rtl'|'ltr'} locale.dir - text direction.
   * @returns {Promise<void>}
   */
  const updateLocale = async (
    locale = {
      code: 'en',
      lang: 'en-US',
      dir: 'ltr',
    }
  ) => {
    await i18n.setLocale(locale.code)
    document.documentElement.lang = locale.lang
    // Always set `dir` property, default to 'ltr'
    document.documentElement.dir = locale.dir
  }
  /**
   * Show banner inviting to contribute translations if fewer than 90%
   * of strings are translated for current locale.
   * Hard-coded to false for default locales: `en` and `en_US`.
   *
   * @param {import('../locales/scripts/types').i18nLocaleProps} locale - current locale object
   * @returns {boolean}
   */
  const needsTranslationBanner = (locale) => {
    if (['en', 'en_US'].includes(locale)) return false

    return locale.translated <= 90
  }

  const bannerDismissedForLocales = useStorage(
    'openverse-dismissed-banner-locales',
    [],
    {
      serializer: StorageSerializers.object,
    }
  )
  const shouldHideBanner = computed(() => {
    return (
      !showBanner.value ||
      bannerDismissedForLocales.value.includes(bannerLocale.code)
    )
  })
  const dismissBanner = () => {
    bannerDismissedForLocales.value = [
      ...bannerDismissedForLocales.value,
      bannerLocale.code,
    ]
  }
  const translationLink = computed(
    () => `${BASE_URL}${bannerLocale.code}/default/`
  )
  /**
   * Handles messages of type `localeSet` received by the `iframe`. Any
   * other message types will be discarded.
   *
   * It sets the i18n locale property, defaulting to `en` if 0 translations are available for the locale,
   * and shows the translation banner if necessary,
   *
   * @param {string} type - the nature of the message received.
   * @param {Object} value - the data sent with the message.
   * @param {string} value.locale - wpLocale code of the locale, e.g. 'en_US'.
   * @param {string} value.lang - the iso code for language
   * (and sometimes country), e.g. 'en-US'.
   * Default lang value on wp.org is 'en', and on wp.org/openverse - 'en-US'.
   * @param {'rtl'|'ltr'} [value.dir] - the locale text direction.
   */
  const localeMsgHandler = async ({ data: { type, value } }) => {
    if (type !== 'localeSet') return
    // If the locale set by wp.org is 'en_US', not 'en', this is not necessary.
    const wpLocaleValue = value.locale === 'en' ? 'en_US' : value.locale
    let locale = i18n.locales.find((item) => item.wpLocale === wpLocaleValue)
    let htmlLocaleProps
    /**
     * i18n.locales list only contains the locales that have at least one
     * translated string.
     */
    if (locale) {
      htmlLocaleProps = {
        code: locale.code,
        lang: locale.wpLocale.replace('_', '-'),
        dir: locale.dir === 'rtl' ? 'rtl' : 'ltr',
      }
    } else {
      locale = Object.values(untranslatedLocales).find(
        (item) => item.wpLocale === value.locale
      )
    }
    await updateLocale(htmlLocaleProps)

    if (needsTranslationBanner(locale)) {
      showBanner.value = true
      bannerLocale.code = locale.code || null
      bannerLocale.name = locale.name || 'this'
    }
  }

  onMounted(() => {
    window.addEventListener('message', localeMsgHandler)
    sendWindowMessage({
      debug: config.dev,
      type: 'localeGet',
      value: {},
    })
  })
  onUnmounted(() => {
    window.removeEventListener('message', localeMsgHandler)
  })
  return {
    shouldHideBanner,
    dismissBanner,
    bannerLocale,
    translationLink,
  }
}
