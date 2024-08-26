export interface I18nLocaleProps {
  code: string
  name: string
  wpLocale?: string
  file?: string
  /** @deprecated use "language" instead */
  iso?: string
  language?: string
  dir?: string
  translated?: number
}
