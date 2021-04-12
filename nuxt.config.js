import pkg from './package.json'

/**
 * Default environment variables are set on this key. Defaults are fallbacks to existing env vars.
 */
export const env = {
  apiUrl: process.env.API_URL || 'https://api.creativecommons.engineering/v1/',
  socialSharing: process.env.SOCIAL_SHARING || true,
  enableGoogleAnalytics: process.env.ENABLE_GOOGLE_ANALYTICS || false,
  googleAnalyticsUA: process.env.GOOGLE_ANALYTICS_UA || 'UA-2010376-36',
  filterStorageKey: 'ccsearch-filter-visibility',
  enableInternalAnalytics: process.env.ENABLE_INTERNAL_ANALYTICS || false,
}

/**
 * The default metadata for the site. Can be extended and/or overwritten per page. And even in components!
 * See the Nuxt.js docs for more info.
 * {@link https://nuxtjs.org/guides/features/meta-tags-seo Nuxt.js Docs}
 */
const meta = [
  { charset: 'utf-8' },
  {
    name: 'description',
    content:
      'A new Creative Commons search tool for creators seeking to discover and reuse free resources with greater ease.',
  },
  { name: 'viewport', content: 'width=device-width,initial-scale=1' },
  { name: 'twitter:card', content: 'summary_large_image' },
  { name: 'twitter:site', content: '@creativecommons' },
  { name: 'og:title', content: 'Creative Commons' },
  {
    name: 'og:image',
    content: '/cclogo-shared-image.jpg',
  },
  {
    name: 'og:description',
    content:
      'Empowering the world to share through 6 simple licenses + a global community of advocates for open.',
  },
  {
    name: 'og:url',
    content: 'https://creativecommons.org',
  },
  {
    name: 'og:site_name',
    content: 'Creative Search',
  },
  {
    vmid: 'monetization',
    name: 'monetization',
    content: '$ilp.uphold.com/edR8erBDbRyq',
  },
]

if (process.env.NODE_ENV === 'production') {
  meta.push({
    'http-equiv': 'Content-Security-Policy',
    content: 'upgrade-insecure-requests',
  })
}

// Default html head
const head = {
  title: 'CC Search',
  meta,
  link: [
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
      title: 'CC Search',
      href: '/opensearch.xml',
    },
    {
      rel: 'icon',
      type: 'image/png',
      href: '/app-icons/cc-site-icon-150x150.png',
      sizes: '32x32',
    },
    {
      rel: 'icon',
      type: 'image/png',
      href: '/app-icons/cc-site-icon-300x300.png',
      sizes: '192x192',
    },
    {
      rel: 'apple-touch-icon-precomposed',
      type: 'image/png',
      href: '/app-icons/cc-site-icon-300x300.png',
      sizes: '192x192',
    },
  ],
}

export default {
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
  server: { port: process.env.PORT || 8443 },
  components: {
    dirs: [
      '~/components',
      '~/components/ContentReport',
      '~/components/Filters',
      '~/components/ImageDetails',
      '~/components/MetaSearch',
    ],
  },
  plugins: [
    '~/plugins/i18n.js',
    { src: '~/plugins/ab-test-init.js', mode: 'client' },
    { src: '~plugins/ga.js', mode: 'client' },
  ],
  css: [
    '@creativecommons/vocabulary/scss/vocabulary.scss',
    '~/styles/global.scss',
  ],
  head,
  env,
  buildModules: ['@nuxtjs/svg', '@nuxtjs/eslint-module'],
  modules: ['@nuxtjs/sentry', '@nuxtjs/sitemap', 'nuxt-ssr-cache'],
  sentry: {
    dsn:
      process.env.SENTRY_DSN ||
      'https://3f3e05dbe6994c318d1bf1c8bfcf71a1@o288582.ingest.sentry.io/1525413',
    lazy: true,
  },
}
