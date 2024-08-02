import { defineNuxtConfig } from "nuxt/config"

import { disallowedBots } from "./src/constants/disallowed-bots"
import locales from "./src/locales/scripts/valid-locales.json"

import type { LocaleObject } from "@nuxtjs/i18n"

/**
 * This configuration sets values necessary at *build time*
 * to build the app and prerender our pages.
 *
 * Pay special attention when setting runtimeConfig values
 * in this file.
 *
 * Any key in `{runtimeConfig: {}}` can be
 * overwritten with a NUXT_ environment variable,
 * with the camelCase key converted to SCREAMING_SNAKE_CASE.
 *
 * The runtimeConfig values here are either defaults for local
 * development, or placeholders used to register the NUXT_
 * environment variables.
 *
 * See our .env.template for a definitive list of runtime values.
 *
 * Do not use import.meta.env to retrieve environment variables
 * here without careful consideration.
 *
 * @see {@link https://nuxt.com/docs/guide/going-further/runtime-config#example}
 */
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
  // Remember: Can be overwritten by NUXT_* env vars
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    // Remember: Can be overwritten by NUXT_PUBLIC_* env vars
    public: {
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
  /**
   * Robots.txt rules are configured here via the \@nuxtjs/robots package.
   * @see {@link https://nuxtseo.com/robots/guides/nuxt-config|Robots Config Rules}
   */
  robots: {
    disallow: ["/search", "/search/audio", "/search/image"],
    groups: [
      ...disallowedBots.map((bot) => ({
        userAgent: [bot],
        disallow: ["/"], // block bots from all routes
      })),
    ],
  },
  tailwindcss: {
    cssPath: "~/styles/tailwind.css",
  },
  i18n: {
    locales: [
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
    ].filter((l) => Boolean(l.iso)) as LocaleObject[],
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
    // `trackLocalhost` is deprecated, but the replacement `ignoredHostnames: []`
    // has a bug, @see https://github.com/nuxt-modules/plausible/issues/30
    trackLocalhost: true,
  },
})
