import { isProd } from "./node-env"

import type { ModuleConfiguration } from "@nuxtjs/sentry"

/**
 * Get the Sentry configuration based on the current environment.
 * @param isDisabled - whether to disable Sentry
 * @returns the Sentry configuration to use
 */
export const sentryConfig: ModuleConfiguration = {
  dsn: process.env.SENTRY_DSN,
  disabled: process.env.DISABLE_SENTRY
    ? true
    : process.env.SENTRY_DSN === undefined || !isProd,
  logMockCalls: false,
  lazy: true,
  clientConfig: {
    // Only allow errors that come from openverse.org or a subdomain
    allowUrls: [/^https?:\/\/((.*)\.)?openverse\.org/],
  },
  config: {
    ignoreErrors: [
      // Ignore browser extension errors
      /window\.bannerNight/,

      // Ignore errant focus-trap-vue errors
      /`initialFocus` did not return a node/,

      // Cloudflare
      /sendBeacon/,

      // Local errors
      /__webpack_hmr\/modern/,
    ],
  },
}
