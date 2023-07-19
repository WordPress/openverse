import type { LocaleObject } from "@nuxtjs/i18n"

export type TranslationBannerId = `translation-${LocaleObject["code"]}`
export type BannerId = TranslationBannerId | "analytics"
