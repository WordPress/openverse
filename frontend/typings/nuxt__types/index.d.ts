declare module "@nuxtjs/i18n" {
  /**
   * We put a little extra information in the Vue-i18n `locales` field such as the
   * locale's name and native name, which comes in use here.
   */
  export interface LocaleObject {
    name: string
    nativeName: string
    translated: number
  }
}

export {}
