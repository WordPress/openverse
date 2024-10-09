import { defineNuxtConfig } from "nuxt/config"

import { disallowedBots } from "./src/constants/disallowed-bots"
import locales from "./src/locales/scripts/valid-locales.json"

import type { LocaleObject } from "@nuxtjs/i18n"

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
  /**
   * Define available runtime configuration values and their defaults.
   *
   * See linked documentation for details, including how to override defaults
   * with runtime values using environment variables.
   *
   * @see {@link https://nuxt.com/docs/api/nuxt-config#runtimeconfig-1}
   */
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    public: {
      deploymentEnv: "local",
      apiUrl: "https://api.openverse.org/",
      savedSearchCount: 4,
      site: {
        trailingSlash: false,
      },
      sentry: {
        dsn: "",
        environment: "local",
        // Release is a build time variable, and as such, is defined in app.config.ts
      },
      plausible: {
        ignoredHostnames: ["localhost", "staging.openverse.org"],
        logIgnoredEvents: true,
        apiHost: "http://localhost:50290",
        domain: "localhost",
      },
    },
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
    "@nuxtjs/storybook",
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
   * @see {@link https://nuxtseo.com/robots/guides/nuxt-config}
   */
  robots: {
    disallow: [
      // robots rules are prefixed-based, so there's no need to configure specific media type searches
      "/search",
      // Other routes have more complex requirements; we configure those with `useRobotsRule` as needed
    ],
    groups: [
      ...disallowedBots.map((bot) => ({
        userAgent: [bot],
        disallow: ["/"], // block disallowed bots from all routes
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
        language: "en", // used for SEO purposes (html lang attribute)
        isCatchallLocale: true, // the catchall locale for `en` locales

        /* Custom fields */

        name: "English",
        nativeName: "English",
      },
      ...locales,
    ].filter((l) => Boolean(l.language)) as LocaleObject[],
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
  /**
   * Workaround for https://github.com/nuxt-modules/storybook/issues/776
   * TODO: remove after Storybook v8.4 is released.
   */
  storybook: {
    port: 54000,
  },
  vite: {
    optimizeDeps: {
      include: ["jsdoc-type-pratt-parser"],
    },
  },
})
