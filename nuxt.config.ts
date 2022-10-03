import path from 'path'
import fs from 'fs'

import promBundle from 'express-prom-bundle'

import pkg from './package.json'
import locales from './src/locales/scripts/valid-locales.json'

import { searchTypes } from './src/constants/media'
import { VIEWPORTS } from './src/constants/screens'

import { isProd } from './src/utils/node-env'
import { sentryConfig } from './src/utils/sentry-config'
import { env } from './src/utils/env'

import type { NuxtConfig, ServerMiddleware } from '@nuxt/types'
import type { LocaleObject } from '@nuxtjs/i18n'
import type { IncomingMessage, NextFunction } from 'connect'
import type http from 'http'

/**
 * The default metadata for the site. Can be extended and/or overwritten per page. And even in components!
 * See the Nuxt.js docs for more info.
 * {@link https://nuxtjs.org/guides/features/meta-tags-seo} Nuxt.js Docs
 */
const meta = [
  { charset: 'utf-8' },
  {
    name: 'viewport',
    content: 'width=device-width,initial-scale=1',
  },
  // Tells Google to only crawl Openverse when iframed
  { hid: 'googlebot', name: 'googlebot', content: 'noindex,indexifembedded' },
  {
    vmid: 'monetization',
    name: 'monetization',
    content: '$ilp.uphold.com/edR8erBDbRyq',
  },
  {
    hid: 'theme-color',
    name: 'theme-color',
    content: '#ffffff',
  },
  {
    name: 'description',
    content:
      'Search over 600 million free and openly licensed images, photos, audio, and other media types for reuse and remixing.',
  },
  { hid: 'og:title', name: 'og:title', content: 'Openverse' },
  {
    hid: 'og:image',
    name: 'og:image',
    content: '/openverse-default.jpg',
  },
  {
    hid: 'og:description',
    name: 'og:description',
    content:
      'Search over 600 million free and openly licensed images, photos, audio, and other media types for reuse and remixing.',
  },
  { name: 'twitter:card', content: 'summary_large_image' },
  { name: 'twitter:site', content: '@WPOpenverse' },
]

if (process.env.NODE_ENV === 'production') {
  meta.push({
    // @ts-expect-error: 'http-equiv' isn't allowed here by Nuxt
    'http-equiv': 'Content-Security-Policy',
    content: 'upgrade-insecure-requests',
  })
}

const favicons = [
  // SVG favicon
  {
    rel: 'icon',
    href: '/openverse-logo.svg',
  },
  // SVG favicon for Safari
  {
    rel: 'mask-icon',
    href: '/opvenverse-logo.svg',
    color: '#30272E',
  },
  // Fallback iPhone Icon
  {
    rel: 'apple-touch-icon',
    href: '/openverse-logo-180.png',
  },
]

// Default html head
const head = {
  title: 'Openly Licensed Images, Audio and More | Openverse',
  meta,
  link: [
    ...favicons,
    {
      rel: 'preconnect',
      href: env.apiUrl,
      crossorigin: '',
    },
    {
      rel: 'dns-prefetch',
      href: env.apiUrl,
    },
    {
      rel: 'search',
      type: 'application/opensearchdescription+xml',
      title: 'Openverse',
      href: '/opensearch.xml',
    },
  ],
}

const baseProdName = process.env.CI ? '[name]' : '[contenthash:7]'

const filenames: NonNullable<NuxtConfig['build']>['filenames'] = {
  app: ({ isDev, isModern }) =>
    isDev
      ? `[name]${isModern ? '.modern' : ''}.js`
      : `${baseProdName}${isModern ? '.modern' : ''}.js`,
  chunk: ({ isDev, isModern }) =>
    isDev
      ? `[name]${isModern ? '.modern' : ''}.js`
      : `${baseProdName}${isModern ? '.modern' : ''}.js`,
  css: ({ isDev }) => (isDev ? '[name].css' : `css/${baseProdName}.css`),
  img: ({ isDev }) =>
    isDev ? '[path][name].[ext]' : `img/${baseProdName}.[ext]`,
  font: ({ isDev }) =>
    isDev ? '[path][name].[ext]' : `fonts/${baseProdName}.[ext]`,
  video: ({ isDev }) =>
    isDev ? '[path][name].[ext]' : `videos/${baseProdName}.[ext]`,
}

const config: NuxtConfig = {
  // eslint-disable-next-line no-undef
  version: pkg.version, // used to purge cache :)
  cache: {
    pages: ['/'],
    store: {
      type: 'memory', // 'redis' would be nice
      max: 100,
      ttl: process.env.MICROCACHE_DURATION || 60,
    },
  },
  srcDir: 'src/',
  modern: 'client',
  server: {
    port: process.env.PORT || 8443,
    https: process.env.LOCAL_SSL
      ? {
          key: fs.readFileSync(path.resolve(__dirname, 'localhost+1-key.pem')),
          cert: fs.readFileSync(path.resolve(__dirname, 'localhost+1.pem')),
        }
      : undefined,
  },
  router: {
    middleware: 'middleware',
  },
  components: [
    { path: '~/components', extensions: ['vue'], pathPrefix: false },
  ],
  plugins: [
    '~/plugins/url-change.ts',
    '~/plugins/migration-notice.ts',
    '~/plugins/ua-parse.ts',
    '~/plugins/focus-visible.client.ts',
    '~/plugins/api-token.server.ts',
  ],
  css: ['~/styles/tailwind.css', '~/assets/fonts.css', '~/styles/accent.css'],
  head,
  env, // TODO: Replace with `publicRuntimeConfig`
  privateRuntimeConfig: {
    apiClientId: process.env.API_CLIENT_ID,
    apiClientSecret: process.env.API_CLIENT_SECRET,
  },
  dev: !isProd,
  buildModules: [
    '@nuxt/typescript-build',
    '@nuxtjs/composition-api/module',
    '@nuxt/postcss8',
    '@nuxtjs/style-resources',
    '@nuxtjs/svg',
    '@nuxtjs/eslint-module',
    '@pinia/nuxt',
  ],
  modules: [
    'portal-vue/nuxt',
    '@nuxtjs/i18n',
    '@nuxtjs/redirect-module',
    '@nuxtjs/sentry',
    '@nuxtjs/sitemap',
    'cookie-universal-nuxt',
  ],
  serverMiddleware: [
    { path: '/healthcheck', handler: '~/server-middleware/healthcheck.js' },
  ],
  i18n: {
    locales: [
      {
        // unique identifier for the locale in Vue i18n
        code: 'en',
        name: 'English',
        nativeName: 'English',
        // ISO code used for SEO purposes (html lang attribute)
        iso: 'en',
        // wp_locale as found in GlotPress
        wpLocale: 'en_US',
        file: 'en.json',
      },
      ...(locales ?? []),
    ].filter((l) => Boolean(l.iso)) as LocaleObject[],
    lazy: true,
    langDir: 'locales',
    defaultLocale: 'en',
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
    vueI18n: '~/plugins/vue-i18n',
  },
  /**
   * Map the old route for /photos/_id page to /image/_id permanently to keep links working.
   * See the redirect module for more info.
   * {@link https://github.com/nuxt-community/redirect-module#usage}
   */
  redirect: {
    rules: [
      { from: '^/photos/(.*)$', to: '/image/$1', statusCode: 301 },
      { from: '/meta-search', to: '/external-sources', statusCode: 301 },
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
  hooks: {
    render: {
      /**
       * When modifying this function in development with automatic rebuilds enabled
       * it _will_ crash your server with an error about duplicate metric name registration.
       * To debug this function's behavior locally you will have to tolerate stopping and
       * starting `pnpm dev` between each change to nuxt.config.ts. To prevent this from
       * being a _general_ problem the metrics middleware is disabled in development
       * mode, otherwise any change to `nuxt.config.ts` would cause this crash. If you
       * need to debug metrics locally, comment out the early return in development.
       */
      setupMiddleware: (app) => {
        if (process.env.NODE_ENV === 'development') return

        const bypassMetricsPathParts = [
          /**
           * Exclude static paths. Remove once we've moved static file
           * hosting out of the SSR server's responsibilities.
           */
          '_nuxt',
          /**
           * Only include these paths in development. They do not exist in production
           * so we can happily skip the extra iterations these path parts introduce.
           */
          ...(process.env.NODE_ENV === 'development'
            ? ['__webpack', 'sse']
            : []),
        ]
        /**
         * Register this here so that it's registered at the absolute top
         * of the middleware stack. Using server-middleware puts it
         * after a whole host of stuff.
         *
         * Note: The middleware only has access to server side navigations,
         * as it is indeed an express middleware, not a Nuxt page middleware.
         * There's no safe way to pipe client side metrics to Prometheus with
         * this set up and if we wanted that anyway we'll want to invest into
         * an actual RUM solution, not a systems monitoring solution like
         * Prometheus. The implication of this is that the metrics will only
         * include SSR'd requests. SPA navigations or anything else that
         * happens exclusively on the client will not be measured. This is the
         * expected behavior!
         *
         * @see {@link https://github.com/nuxt/nuxt.js/blob/dev/packages/server/src/server.js#L70-L138}
         */
        app.use(
          promBundle({
            bypass: (req) =>
              bypassMetricsPathParts.some((p) => req.originalUrl.includes(p)),
            includeMethod: true,
            includePath: true,
            normalizePath: [
              ...searchTypes.map(
                // Normalize single result pages with IDs in the path
                (t) => [`/${t}/.*`, `/${t}/#id`] as [string, string]
              ),
            ],
            /**
             * promBundle creates an Express middleware function, which is type-incompatible
             * with Nuxt's "connect" middleware functions. I guess they _are_ compatible,
             * in actual code, or maybe just in the particular implementation of the prometheus
             * bundle middleware. In any case, this cast is necessary to appeas TypeScript
             * without an ugly ts-ignore.
             */
          }) as unknown as ServerMiddleware
        )
      },
    },
  },
  build: {
    templates: [
      {
        src: './nuxt-template-overrides/App.js',
        dst: 'App.js',
      },
      {
        src: './nuxt-template-overrides/index.js',
        dst: 'index.js',
      },
    ],
    filenames,
    friendlyErrors: false,
    postcss: {
      plugins: {
        tailwindcss: {},
        autoprefixer: {},
        'postcss-focus-visible': {},
      },
    },
    extend(config, ctx) {
      // Enables use of IDE debuggers
      config.devtool = ctx.isClient ? 'source-map' : 'inline-source-map'

      // Mitigates import errors for Pinia
      config.module?.rules.push({
        test: /\.mjs$/,
        include: /node_modules/,
        type: 'javascript/auto',
      })
    },
  },
  storybook: {
    port: 6006, // standard port for Storybook
    stories: ['~/**/*.stories.@(mdx|js)'],
    addons: [
      {
        name: '@storybook/addon-essentials',
        options: {
          backgrounds: false,
          viewport: true,
          toolbars: true,
        },
      },
    ],
    parameters: {
      options: {
        storySort: {
          order: ['Introduction', ['Openverse UI']],
        },
      },
      viewport: {
        viewports: VIEWPORTS,
      },
    },
  },
}

export default config
