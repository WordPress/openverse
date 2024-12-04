export type TextDirection = "ltr" | "rtl"

/**
 * These properties are available in the GlotPress source code:
 * https://raw.githubusercontent.com/GlotPress/GlotPress/refs/heads/develop/locales/locales.php
 * They are used to generate the metadata that the Nuxt app uses, `I18nLocaleProps`.
 */
export interface RawI18nLocaleProps {
  name: string
  nativeName: string
  /** The WordPress locale code that is used as the locale's URL prefix */
  slug: string
  textDirection: TextDirection
  nplurals?: number
  pluralExpression?: string
}

export interface RawI18nLocalePropsWithPlurals
  extends Omit<RawI18nLocaleProps, "nplurals" | "pluralExpression"> {
  nplurals: number
  /**
   * The plural expression used for custom pluralization, ee the `vue-i18n.ts` settings file
   */
  pluralExpression: string
}

type LocaleCode = string

export interface I18nLocaleProps {
  name: string
  nativeName: string
  code: LocaleCode
  dir: TextDirection
  file: `${LocaleCode}.json`
  language: string
  translated: number
}

export interface JsonEntry {
  key: string
  value: string
  doc: string
}

export interface LocalesByTranslation {
  translated: I18nLocaleProps[]
  untranslated: I18nLocaleProps[]
}
