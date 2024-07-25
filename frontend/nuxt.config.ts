import { defineNuxtConfig } from "nuxt/config"

import locales from "./src/locales/scripts/valid-locales.json"
import { meta as commonMeta } from "./src/constants/meta"

import type { LocaleObject } from "@nuxtjs/i18n"

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
  disallow: ["/search/audio/", "/search/image/", "/search/"],
  groups: [
    ...disallowedBots.map((bot) => ({
      userAgent: [bot],
      disallow: ["/"], // block bots from all routes
    })),
  ],
}

const isProductionBuild = import.meta.env.NODE_ENV === "production"
const isPlaywright = import.meta.env.PW === "true"
const isProdNotPlaywright = isProductionBuild && !isPlaywright
const isTest = import.meta.env.TEST === "true"

const apiUrl =
  import.meta.env.NUXT_PUBLIC_API_URL || "https://api.openverse.org/"

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
          href: apiUrl,
        },
        {
          rel: "preconnect",
          href: apiUrl,
          crossorigin: "",
        },
      ],
    },
  },
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
      apiUrl,
      providerUpdateFrequency: 3600000,
      savedSearchCount: 4,
      sentry: {
        dsn: "",
        environment: import.meta.env.DEPLOYMENT_ENV ?? "local",
        release: import.meta.env.SEMANTIC_VERSION,
      },
      isPlaywright,
    },
  },
  site: {
    indexable: isProdNotPlaywright,
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
    baseUrl: import.meta.env.SITE_URL,
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
    enabled: !isTest,
    logIgnoredEvents: !isProductionBuild,
    trackLocalhost: !isProdNotPlaywright,
    autoPageviews: isProdNotPlaywright,
    domain: import.meta.env.SITE_DOMAIN,
    apiHost: import.meta.env.PLAUSIBLE_SITE_URL,
  },
})
