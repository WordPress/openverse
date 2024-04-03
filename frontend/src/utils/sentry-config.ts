import type { ModuleOptions } from "@nuxtjs/sentry"

/**
 * Get the Sentry configuration based on the current environment.
 * @param isDisabled - whether to disable Sentry
 * @returns the Sentry configuration to use
 */
export const sentryConfig: ModuleOptions = {
  dsn: process.env.SENTRY_DSN,
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
      /mce-visual-caret-hidden/,

      // Ignore errant focus-trap-vue errors
      /`initialFocus` did not return a node/,

      // Ignore ResizeObserver loop-related errors
      /ResizeObserver loop limit exceeded/,
      /ResizeObserver loop completed with undelivered notifications/,

      // Cloudflare
      /sendBeacon/,

      // Local errors
      /__webpack_hmr\/modern/,
    ],
  },
}
