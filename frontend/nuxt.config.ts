import { defineNuxtConfig } from "nuxt/config"

import locales from "./src/locales/scripts/valid-locales.json"

import { isProd } from "./src/utils/node-env"
import { env } from "./src/utils/env"

import type { LocaleObject } from "vue-i18n-routing"

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
  ...(locales ?? []),
].filter((l) => Boolean(l.iso)) as LocaleObject[]

const isProdNotPlaywright = isProd && !(process.env.PW === "true")

export default defineNuxtConfig({
  srcDir: "src/",
  devServer: {
    port: 8443,
    host: "0.0.0.0",
  },
  imports: {
    autoImport: false,
  },
  css: ["~/assets/fonts.css", "~/styles/accent.css"],
  env, // TODO: Replace with `publicRuntimeConfig`
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    public: {
      apiUrl: "https://api.openverse.engineering/",
      sentry: {
        dsn: "",
        environment: "development",
      },
      plausible: {
        trackLocalhost: true, // Replace with isProdNotPw
        // This is the current domain of the site.
        domain:
          process.env.SITE_DOMAIN ??
          (isProdNotPlaywright ? "openverse.org" : "localhost"),
        apiHost:
          process.env.SITE_DOMAIN ??
          (isProdNotPlaywright
            ? "https://openverse.org"
            : /**
               * We rely on the Nginx container running as `frontend_nginx`
               * in the local compose stack to proxy requests. Therefore, the
               * URL here is not for the Plausible container in the local stack,
               * but the Nginx service, which then itself forwards the requests
               * to the local Plausible instance.
               *
               * In production, the Nginx container is handling all requests
               * made to the root URL (openverse.org), and is configured to
               * forward Plausible requests to upstream Plausible.
               */
              "http://localhost:50290"),
      },
    },
  },
  dev: !isProd,
  modules: [
    "@pinia/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/svg-sprite",
    "@nuxtjs/plausible",
    "@nuxt/test-utils/module",
  ],
  svgSprite: {
    input: "~/assets/svg/raw",
    output: "~/assets/svg/sprite",
  },
  tailwindcss: {
    cssPath: "~/styles/tailwind.css",
  },
  i18n: {
    baseUrl: "https://openverse.org",
    locales: openverseLocales,
    lazy: true,
    langDir: "locales",
    defaultLocale: "en",
    /**
     * `detectBrowserLanguage` must be false to prevent nuxt/i18n from automatically
     * setting the locale based on headers or the client-side `navigator` object.
     *
     * Such detection is handled at the parent level in WP.org.
     *
     * More info about the Nuxt i18n:
     *
     * - [detectBrowserLanguage](https://i18n.nuxtjs.org/options-reference/#detectbrowserlanguage)
     * - [Browser language detection info](https://i18n.nuxtjs.org/browser-language-detection)
     * */
    detectBrowserLanguage: false,
    vueI18n: "./src/vue-i18n",
  },
})
