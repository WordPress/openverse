import type { LocaleObject } from "vue-i18n-routing"

export type TranslationBannerId = `translation-${LocaleObject["code"]}`
export type BannerId = TranslationBannerId | "analytics"
