import type { LocaleObject } from "vue-i18n-routing"

const BASE_URL = "https://translate.wordpress.org/projects/meta/openverse/"
// We show the banner if the translation is less than this percentage
const MINIMUM_TRANSLATION_PERCENTAGE = 90

export const needsTranslationBanner = (locale: LocaleObject) => {
  if (!locale || locale.code === "en") {
    return false
  }

  return (locale.translated ?? 100) <= MINIMUM_TRANSLATION_PERCENTAGE
}

export const createTranslationLink = (locale: LocaleObject) =>
  `${BASE_URL}${locale.code || "en"}/default/`
