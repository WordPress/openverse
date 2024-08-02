import { defineNuxtConfig } from "nuxt/config"

import locales from "./src/locales/scripts/valid-locales.json"

import type { LocaleObject } from "@nuxtjs/i18n"

const disallowedBots = [
  "GPTBot",
  "CCBot",
  "ChatGPT-User",
  "Google-Extended",
  "anthropic-ai",
  "Omgilibot",
  "Omgili",
  "FacebookBot",
  "Diffbot",
  "Bytespider",
  "ImagesiftBot",
  "cohere-ai",
]

/**
 * Robots.txt rules are configured here via the \@nuxtjs/robots package.
 * @see {@link https://nuxtseo.com/robots/guides/nuxt-config|Robots Config Rules}
 */
const robots = {
  userAgent: "*",
  disallow: ["/search", "/search/audio", "/search/image"],
  groups: [
    ...disallowedBots.map((bot) => ({
      userAgent: [bot],
      disallow: ["/"], // block bots from all routes
    })),
  ],
}

const openverseLocales = [
  {
    /* Nuxt i18n fields */

    code: "en", // unique identifier for the locale in Vue i18n
    dir: "ltr",
    file: "en.json",
    iso: "en", // used for SEO purposes (html lang attribute)

    /* Custom fields */

    name: "English",
    nativeName: "English",
  },
  ...locales,
].filter((l) => Boolean(l.iso)) as LocaleObject[]

export default defineNuxtConfig({
  srcDir: "src/",
  serverDir: "server/",
  devServer: {
    port: 8443,
    host: "0.0.0.0",
  },
  imports: {
    autoImport: false,
  },
  compatibilityDate: "2024-07-23",
  css: ["~/assets/fonts.css", "~/styles/accent.css"],
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    public: {
      // These values can be overridden by the NUXT_PUBLIC_* env variables
      deploymentEnv: "local",
      apiUrl: "https://api.openverse.org/",
      providerUpdateFrequency: 3600000,
      savedSearchCount: 4,
      sentry: {
        dsn: "",
        environment: "local",
        release: import.meta.env.SEMANTIC_VERSION,
      },
    },
  },
  site: {
    trailingSlash: false,
  },
  /**
   * Disable debug mode to prevent excessive timing logs.
   */
  debug: false,
  experimental: {
    /**
     * Improve router performance, see https://nuxt.com/blog/v3-10#%EF%B8%8F-build-time-route-metadata
     */
    scanPageMeta: true,
  },
  modules: [
    "@pinia/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/plausible",
    "@nuxt/test-utils/module",
    "@nuxtjs/sitemap",
    "@nuxtjs/robots",
  ],
  routeRules: {
    "/photos/**": { redirect: { to: "/image/**", statusCode: 301 } },
    "/meta-search": { redirect: { to: "/about", statusCode: 301 } },
    "/external-sources": { redirect: { to: "/about", statusCode: 301 } },
  },
  robots,
  tailwindcss: {
    cssPath: "~/styles/tailwind.css",
  },
  i18n: {
    locales: openverseLocales,
    lazy: true,
    langDir: "locales",
    defaultLocale: "en",
    /**
     * `detectBrowserLanguage` must be false to prevent nuxt/i18n from automatically
     * setting the locale based on headers or the client-side `navigator` object.
     *
     * More info about the Nuxt i18n:
     *
     * - [Browser language detection info](https://i18n.nuxtjs.org/docs/guide/browser-language-detection)
     * */
    detectBrowserLanguage: false,
    trailingSlash: false,
    vueI18n: "./src/vue-i18n",
  },
  plausible: {
    trackLocalhost: true,
  },
})
