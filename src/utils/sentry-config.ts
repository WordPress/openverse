import { isProd } from './node-env'

import type { ModuleConfiguration } from '@nuxtjs/sentry'

/**
 * Get the Sentry configuration based on the current environment.
 * @param isDisabled - whether to disable Sentry
 * @returns the Sentry configuration to use
 */
export const sentryConfig: ModuleConfiguration = {
  dsn:
    process.env.SENTRY_DSN ||
    'https://53da8fbcebeb48a6bf614a212629df6b@o787041.ingest.sentry.io/5799642',
  disabled: !isProd,
  lazy: true,
  clientConfig: {
    // Only allow errors that come from an actual openverse.engineering subdomain
    allowUrls: [/^https?:\/\/(.*)\.openverse\.engineering/],
  },
  config: {
    ignoreErrors: [
      // Ignore browser extension errors
      /window\.bannerNight/,

      // Ignore errant focus-trap-vue errors
      /`initialFocus` did not return a node/,

      // Cloudflare
      /sendBeacon/,
    ],
  },
}
