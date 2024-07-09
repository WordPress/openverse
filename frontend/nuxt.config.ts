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

const isProd = import.meta.env.NODE_ENV === "production"
const isPlaywright = import.meta.env.PW === "true"
const isProdNotPlaywright = isProd && !isPlaywright
const isTest = import.meta.env.TEST === "true"

const apiUrl =
  import.meta.env.NUXT_PUBLIC_API_URL || "https://api.openverse.org/"
const plausibleSiteDomain = import.meta.env.SITE_DOMAIN

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
  css: ["~/assets/fonts.css", "~/styles/accent.css"],
  runtimeConfig: {
    apiClientId: "",
    apiClientSecret: "",
    public: {
      deploymentEnv: process.env.DEPLOYMENT_ENV ?? "local",
      // Can be overwritten by NUXT_PUBLIC_API_URL env variable
      apiUrl,
      providerUpdateFrequency: 3600000,
      savedSearchCount: 4,
      sentry: {
        dsn: isProdNotPlaywright
          ? "https://b6466b74788a4a2f8a7912eea912beb7@o787041.ingest.sentry.io/5799642"
          : "",
        environment: isProd ? "production" : "local",
        release: "",
      },
      isPlaywright,
    },
  },
  site: {
    trailingSlash: true,
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
  ],
  routeRules: {
    "/photos/**": { redirect: { to: "/image/**", statusCode: 301 } },
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
    logIgnoredEvents: !isProd,
    trackLocalhost: !isProdNotPlaywright,
    autoPageviews: isProdNotPlaywright,
    // This is the current domain of the site.
    domain:
      plausibleSiteDomain ??
      (isProdNotPlaywright ? "openverse.org" : "localhost"),
    apiHost:
      plausibleSiteDomain ??
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
})
