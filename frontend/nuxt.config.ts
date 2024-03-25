import path from "path"
import fs from "fs"

import pkg from "./package.json"
import locales from "./src/locales/scripts/valid-locales.json"

import { meta } from "./src/constants/meta"
import { VIEWPORTS } from "./src/constants/screens"

import { isProd } from "./src/utils/node-env"
import { sentryConfig } from "./src/utils/sentry-config"
import { env } from "./src/utils/env"

import type http from "http"

import type { NuxtConfig } from "@nuxt/types"
import type { LocaleObject } from "@nuxtjs/i18n"
import type { IncomingMessage, NextFunction } from "connect"

if (process.env.NODE_ENV === "production") {
  meta.push({
    // @ts-expect-error: 'http-equiv' isn't allowed here by Nuxt
    "http-equiv": "Content-Security-Policy",
    content: "upgrade-insecure-requests",
  })
}

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

// Default html head
const head = {
  title: "Openly Licensed Images, Audio and More | Openverse",
  meta,
  link: [
    ...favicons,
    {
      rel: "preconnect",
      href: env.apiUrl,
      crossorigin: "",
    },
    {
      rel: "dns-prefetch",
      href: env.apiUrl,
    },
    {
      rel: "search",
      type: "application/opensearchdescription+xml",
      title: "Openverse",
      href: "/opensearch.xml",
    },
  ],
}

const baseProdName = process.env.CI ? "[name]" : "[contenthash:7]"

const filenames: NonNullable<NuxtConfig["build"]>["filenames"] = {
  app: ({ isDev, isModern }) =>
    isDev
      ? `[name]${isModern ? ".modern" : ""}.js`
      : `${baseProdName}${isModern ? ".modern" : ""}.js`,
  chunk: ({ isDev, isModern }) =>
    isDev
      ? `[name]${isModern ? ".modern" : ""}.js`
      : `${baseProdName}${isModern ? ".modern" : ""}.js`,
  css: ({ isDev }) => (isDev ? "[name].css" : `css/${baseProdName}.css`),
  img: ({ isDev }) =>
    isDev ? "[path][name].[ext]" : `img/${baseProdName}.[ext]`,
  font: ({ isDev }) =>
    isDev ? "[path][name].[ext]" : `fonts/${baseProdName}.[ext]`,
  video: ({ isDev }) =>
    isDev ? "[path][name].[ext]" : `videos/${baseProdName}.[ext]`,
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
  ...(locales ?? []),
].filter((l) => Boolean(l.iso)) as LocaleObject[]

const port = process.env.PORT || 8443
const isProdNotPlaywright = isProd && !(process.env.PW === "true")

const config: NuxtConfig = {
  // eslint-disable-next-line no-undef
  version: pkg.version, // used to purge cache :)
  cache: {
    pages: ["/"],
    store: {
      type: "memory", // 'redis' would be nice
      max: 100,
      ttl: process.env.MICROCACHE_DURATION || 60,
    },
  },
  srcDir: "src/",
  modern: "client",
  server: {
    port,
    https: process.env.LOCAL_SSL
      ? {
          key: fs.readFileSync(path.resolve(__dirname, "localhost+1-key.pem")),
          cert: fs.readFileSync(path.resolve(__dirname, "localhost+1.pem")),
        }
      : undefined,
  },
  router: {
    middleware: "middleware",
  },
  components: [
    { path: "~/components", extensions: ["vue"], pathPrefix: false },
  ],
  plugins: [
    "~/plugins/ua-parse.ts",
    "~/plugins/focus-visible.client.ts",
    "~/plugins/api-token.server.ts",
    "~/plugins/polyfills.client.ts",
    "~/plugins/sentry.ts",
    "~/plugins/analytics.ts",
    "~/plugins/errors.ts",
  ],
  css: ["~/assets/fonts.css", "~/styles/tailwind.css", "~/styles/accent.css"],
  head,
  env, // TODO: Replace with `publicRuntimeConfig`
  privateRuntimeConfig: {
    apiClientId: process.env.API_CLIENT_ID,
    apiClientSecret: process.env.API_CLIENT_SECRET,
  },
  dev: !isProd,
  buildModules: [
    "@nuxt/typescript-build",
    "@nuxtjs/composition-api/module",
    "@nuxtjs/svg-sprite",
    "@pinia/nuxt",
  ],
  modules: [
    "portal-vue/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/proxy",
    "@nuxtjs/redirect-module",
    "@nuxtjs/sentry",
    "cookie-universal-nuxt",
    "vue-plausible",
    "~/modules/prometheus.ts",
    // Sitemap must be last to ensure that even routes created by other modules are added
    "@nuxtjs/sitemap",
  ],
  serverMiddleware: [
    { path: "/healthcheck", handler: "~/server-middleware/healthcheck.js" },
    { path: "/robots.txt", handler: "~/server-middleware/robots.js" },
  ],
  svgSprite: {
    input: "~/assets/svg/raw",
    output: "~/assets/svg/sprite",
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
    vueI18n: "~/plugins/vue-i18n",
  },
  sitemap: {
    hostname: "https://openverse.org",
    i18n: {
      locales: openverseLocales.map((l) => l.iso),
      routesNameSeparator: "___",
    },
  },
  /**
   * Map the old route for /photos/_id page to /image/_id permanently to keep links working.
   * See the redirect module for more info.
   * {@link https://github.com/nuxt-community/redirect-module#usage}
   */
  redirect: {
    rules: [
      { from: "^/photos/(.*)$", to: "/image/$1", statusCode: 301 },
      { from: "/meta-search", to: "/about", statusCode: 301 },
      { from: "/external-sources", to: "/about", statusCode: 301 },
    ],
    // If the URL cannot be decoded, we call next() to show the client-side error page.
    onDecodeError: (
      _error: Error,
      _req: IncomingMessage,
      _res: http.ServerResponse,
      next: NextFunction
    ) => {
      return next()
    },
  },
  sentry: sentryConfig,
  build: {
    templates: [
      {
        src: "./nuxt-template-overrides/App.js",
        dst: "App.js",
      },
      {
        src: "./nuxt-template-overrides/index.js",
        dst: "index.js",
      },
    ],
    filenames,
    friendlyErrors: false,
    postcss: {
      postcssOptions: {
        preset: {
          features: {
            // Disable conversion of logical properties to physical properties
            // e.g.: `margin-inline-start` is NOT converted to `margin-left`
            // Necessary for RTL support.
            "logical-properties-and-values": false,
          },
        },
        plugins: {
          tailwindcss: {
            config: path.resolve(__dirname, "tailwind.config.ts"),
          },
          "postcss-focus-visible": {},
        },
      },
    },
    extend(config, ctx) {
      // Enables use of IDE debuggers
      config.devtool = ctx.isClient ? "source-map" : "inline-source-map"
    },
    transpile: [({ isLegacy }) => (isLegacy ? "axios" : undefined)],
  },
  typescript: {
    typeCheck: {
      typescript: {
        configFile: "./tsconfig.json",
        extensions: {
          vue: true,
        },
      },
    },
  },
  storybook: {
    port: 6006, // standard port for Storybook
    stories: ["~/**/*.stories.@(mdx|js)"],
    addons: [
      {
        name: "@storybook/addon-essentials",
        options: {
          backgrounds: true,
          viewport: true,
          toolbars: true,
        },
      },
    ],
    parameters: {
      backgrounds: {
        default: "White",
        values: [
          { name: "White", value: "#ffffff" },
          { name: "Dark charcoal", value: "#30272e" },
        ],
      },
      options: {
        storySort: {
          order: ["Introduction", ["Openverse UI"], "Meta"],
        },
      },
      viewport: {
        viewports: VIEWPORTS,
      },
    },
  },
  plausible: {
    trackLocalhost: !isProdNotPlaywright,
  },
  publicRuntimeConfig: {
    plausible: {
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
    sentry: {
      config: {
        // We need to explicitly configure this for the frontend to have
        // access to it at runtime. On the server side it would be picked
        // up from the environment; the client-side doesn't have that
        // luxury of a configured runtime environment, so we need to
        // tell it what environment it is in.
        environment: process.env.SENTRY_ENVIRONMENT,
      },
    },
  },
}

export default config
