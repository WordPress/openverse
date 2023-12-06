import { computed } from "vue"
import { useContext } from "@nuxtjs/composition-api"

import type { LocaleObject } from "@nuxtjs/i18n"

const BASE_URL = "https://translate.wordpress.org/projects/meta/openverse/"

export function useI18nSync() {
  const { app } = useContext()
  const currentLocale = computed(() => {
    return (app.i18n?.locales as LocaleObject[]).find(
      (item) => item.code === app.i18n.locale
    )
  })

  const needsTranslationBanner = computed(() => {
    if (!currentLocale.value || currentLocale.value.code === "en") {return false}

    return (currentLocale.value?.translated ?? 100) <= 90
  })

  const translationLink = computed(
    () => `${BASE_URL}${currentLocale.value?.code || "en"}/default/`
  )

  return {
    currentLocale,
    needsTranslationBanner,
    translationLink,
  }
}
