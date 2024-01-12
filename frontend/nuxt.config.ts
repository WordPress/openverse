import { defineNuxtConfig } from "nuxt/config"

import { isProd } from "./src/utils/node-env"
import locales from "./src/locales/scripts/valid-locales.json"
import { meta as commonMeta } from "./src/constants/meta"

import type { LocaleObject } from "vue-i18n-routing"

const favicons = [
  // SVG favicon
  {
    rel: "icon",
    href: "/favicon.ico",
  },
  {
    rel: "icon",
    href: "/openverse-logo.svg",
  },
  // SVG favicon for Safari
  {
    rel: "mask-icon",
    href: "/opvenverse-logo.svg",
    color: "#30272E",
  },
  // Fallback iPhone Icon
  {
    rel: "apple-touch-icon",
    href: "/openverse-logo-180.png",
  },
]

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
  app: {
    head: {
      title: "Openly Licensed Images, Audio and More | Openverse",
      meta: commonMeta,
      link: [
        ...favicons,
        {
          rel: "search",
          type: "application/opensearchdescription+xml",
          title: "Openverse",
          href: "/opensearch.xml",
        },
        {
          rel: "dns-prefetch",
          href:
            process.env.NUXT_PUBLIC_API_URL ||
            "https://api.openverse.engineering/",
        },
        {
          rel: "preconnect",
          href:
            process.env.NUXT_PUBLIC_API_URL ||
            "https://api.openverse.engineering/",
          crossorigin: "",
        },
      ],
    },
  },
  srcDir: "src/",
  devServer: {
    port: 8443,
    host: "0.0.0.0",
  },
  imports: {
    autoImport: false,
  },
  css: ["~/assets/fonts.css", "~/styles/accent.css"],
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    public: {
      // Can be overwritten by NUXT_PUBLIC_API_URL env variable
      apiUrl:
        process.env.NUXT_PUBLIC_API_URL || "https://api.openverse.engineering/",
      providerUpdateFrequency: 3600000,
      savedSearchCount: 4,
      sentry: {
        dsn: "",
        environment: process.env.DEPLOYMENT_ENV,
      },
      plausible: {
        trackLocalhost: true, // TODO: Replace with isProdNotPw
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
  /**
   * Disable debug mode to prevent excessive timing logs.
   */
  debug: false,
  modules: [
    "@pinia/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/plausible",
    "@nuxt/test-utils/module",
    "@nuxtjs/sitemap",
  ],
  routeRules: {
    // TODO: Move photos redirect and remove the photos page after this fix:
    // https://github.com/unjs/nitro/pull/1976
    "/meta-search": { redirect: { to: "/about", statusCode: 301 } },
    "/external-sources": { redirect: { to: "/about", statusCode: 301 } },
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
  nitro: {
    prerender: {
      routes: ["/sitemap.xml"],
    },
  },
})
