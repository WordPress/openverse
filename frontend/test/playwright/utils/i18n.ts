import rtlMessages from "~~/test/locales/ar.json"
import esMessages from "~~/test/locales/es.json"
import ruMessages from "~~/test/locales/ru.json"
import enMessages from "~~/i18n/locales/en.json"

const messages: Record<string, Record<string, string>> = {
  ltr: enMessages,
  rtl: rtlMessages,
  es: esMessages,
  ru: ruMessages,
}

/**
 * Simplified i18n t function that returns English messages for `ltr` and Arabic for `rtl`.
 * It can handle nested labels that use the dot notation ('header.title').
 * @param path - The label to translate.
 * @param dir - The language direction.
 * @param locale - If provided, the label will be translated to the given locale.
 */
export const t = (
  path: string,
  dir: LanguageDirection = "ltr",
  locale?: "es" | "ru"
): string => {
  const value = locale
    ? messages[locale][path]
    : messages[dir][path]
      ? messages[dir][path]
      : messages.ltr[path]

  if (!value) {
    throw new Error(
      `Missing translation for "${path}" (locale ${locale}, dir ${dir})`
    )
  }

  return value.replace("{openverse}", "Openverse")
}
export const languageDirections = ["ltr", "rtl"] as const
export type LanguageDirection = (typeof languageDirections)[number]
