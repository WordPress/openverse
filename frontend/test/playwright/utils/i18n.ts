import rtlMessages from "~~/test/locales/ar.json"
import esMessages from "~~/test/locales/es.json"
import ruMessages from "~~/test/locales/ru.json"

import enMessages from "~/locales/en.json"

const messages: Record<string, Record<string, unknown>> = {
  ltr: enMessages,
  rtl: rtlMessages,
  es: esMessages,
  ru: ruMessages,
}
const getNestedProperty = (
  obj: Record<string, unknown>,
  path: string
): string => {
  const value = path
    .split(".")
    .reduce((acc: string | Record<string, unknown>, part) => {
      if (typeof acc === "string") {
        return acc
      }
      if (Object.keys(acc as Record<string, unknown>).includes(part)) {
        return (acc as Record<string, string | Record<string, unknown>>)[part]
      }
      return ""
    }, obj)
  return typeof value === "string" ? value : JSON.stringify(value)
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
  let value = ""
  if (locale) {
    value = getNestedProperty(messages[locale], path)
  } else if (dir === "rtl") {
    value = getNestedProperty(messages.rtl, path)
  }
  return value === "" ? getNestedProperty(messages.ltr, path) : value
}
export const languageDirections = ["ltr", "rtl"] as const
export type LanguageDirection = (typeof languageDirections)[number]
