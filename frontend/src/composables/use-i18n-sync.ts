import { useI18n } from "#imports"

import { computed } from "vue"

import type { LocaleObject } from "vue-i18n-routing"

const BASE_URL = "https://translate.wordpress.org/projects/meta/openverse/"

export function useI18nSync() {
  const i18n = useI18n()
  const currentLocale = computed(() => {
    return (i18n.locales.value as LocaleObject[]).find(
      (item) => item.code === i18n.locale.value
    )
  })

  const needsTranslationBanner = computed(() => {
    if (!currentLocale.value || currentLocale.value.code === "en") {
      return false
    }

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
