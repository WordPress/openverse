import { computed, reactive, useContext } from '@nuxtjs/composition-api'

import { StorageSerializers, useStorage } from '~/composables/use-storage'

const BASE_URL = 'https://translate.wordpress.org/projects/meta/openverse/'

export default function useI18nSync() {
  const { app } = useContext()

  const currentLocale = computed(() => {
    return app.i18n.locales.find((item) => item.code === app.i18n.locale)
  })

  const bannerLocale = reactive({
    code: app.i18n.locale,
    name: currentLocale.value.name,
  })

  /**
   * Show banner inviting to contribute translations if fewer than 90%
   * of strings are translated for current locale.
   * Hard-coded to false for default locales: `en` and `en_US`.
   *
   * @param {string} localeCode - the slug for the current locale. This is the same as the locale `code`.
   * @returns {boolean}
   */
  const needsTranslationBanner = (localeCode) => {
    if (['en'].includes(localeCode)) return false

    let locale = app.i18n.locales.find((item) => item.code === localeCode)

    return !(locale?.translated && locale.translated > 90)
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
      bannerDismissedForLocales.value.includes(bannerLocale.code) ||
      !needsTranslationBanner(bannerLocale.code)
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

  return {
    shouldHideBanner,
    dismissBanner,
    bannerLocale,
    translationLink,
  }
}
