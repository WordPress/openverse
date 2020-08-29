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
  script: [
    {
      hid: 'vocabulary',
      src: 'https://unpkg.com/@creativecommons/vocabulary/js/vocabulary.js',
      defer: true,
      callback: () => {
        if (!document.querySelector('.cc-global-header')) {
          window.vocabulary.createGlobalHeader()
        }
      },
    },
  ],
}

/**
 * Default environment variables are set on this key. Defaults are fallbacks to existing env vars.
 */
const env = {
  apiUrl:
    process.env.API_URL || 'https://api-dev.creativecommons.engineering/v1/',
  socialSharing: process.env.SOCIAL_SHARING || true,
  analyticsId: process.env.GOOGLE_ANALYTICS_UA || 'UA-2010376-36',
  disableAnalytics: process.env.DISABLE_ANALYTICS || false,
  filterStorageKey: 'ccsearch-filter-visibility',
  disableApiAnalytics: process.env.DISABLE_API_ANALYTICS || true,
}

/*
 ** Build configuration (extend key extends webpack)
 */
const build = {
  extend(config, ctx) {
    // Run ESLint on save
    if (ctx.isDev && ctx.isClient) {
      config.module.rules.push({
        enforce: 'pre',
        test: /\.(js|vue)$/,
        loader: 'eslint-loader',
        exclude: /(node_modules)/,
      })
    }
  },
}

export default {
  srcDir: 'src/',
  buildDir: 'dist/',
  components: true,
  plugins: ['~/plugins/i18n.js', { src: '~plugins/ga.js', mode: 'client' }],
  css: ['@creativecommons/vocabulary/scss/vocabulary.scss'],
  head,
  env,
  build,
  buildModules: ['@nuxtjs/svg'],
  modules: ['@nuxtjs/sentry', '@nuxtjs/sitemap'],
  sentry: {
    dsn:
      process.env.SENTRY_DSN ||
      'https://3f3e05dbe6994c318d1bf1c8bfcf71a1@o288582.ingest.sentry.io/1525413',
    lazy: true,
  },
}
