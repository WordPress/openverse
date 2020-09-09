const meta = [
  { charset: 'utf-8' },
  { name: 'viewport', content: 'width=device-width,initial-scale=1' },
  { name: 'twitter:card', content: 'summary_large_image' },
  { name: 'twitter:site', content: '@creativecommons' },
  { name: 'og:title', content: 'Creative Commons' },
  {
    name: 'og:image',
    content: 'https://ccsearch.creativecommons.org/img/cc-logo_large_black.png',
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
    content: 'Creative Commons',
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

export default {
  srcDir: 'src/',
  components: true,
  plugins: ['~/plugins/i18n.js'],
  baseDir: '/src',
  css: ['@creativecommons/vocabulary/scss/vocabulary.scss'],
  head: {
    title: 'CC Search',
    meta,
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
  },
  env: {
    NODE_ENV: 'development',
    API_URL: 'https://api-dev.creativecommons.engineering/v1/',
    SENTRY_DSN:
      'https://3f3e05dbe6994c318d1bf1c8bfcf71a1@o288582.ingest.sentry.io/1525413',
    SOCIAL_SHARING: true,
  },
  buildModules: [
    [
      '@nuxtjs/svg',
      '@nuxtjs/google-analytics',
      {
        id: 'UA-2010376-36', // @todo: Use environment variable to set 'UA-2010376-33' in production
      },
    ],
  ],
  /*
   ** Build configuration
   */
  build: {
    /*
     ** You can extend webpack config here
     */
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
  },
}
