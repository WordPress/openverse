// Use relative import to resolve during nuxt runtime
import stringToBoolean from './string-to-boolean'

/**
 * Default environment variables are set on this key. Defaults are fallbacks to existing env vars.
 * All boolean values should be designed to be false by default.
 */
export const env = {
  apiUrl: process.env.API_URL ?? 'https://api.openverse.engineering/v1/',
  enableGoogleAnalytics: stringToBoolean(process.env.ENABLE_GOOGLE_ANALYTICS),
  googleAnalyticsUA: process.env.GOOGLE_ANALYTICS_UA ?? 'UA-2010376-36',
  filterStorageKey: 'openverse-filter-visibility',
  notificationStorageKey: 'openverse-show-notification',
  enableInternalAnalytics: stringToBoolean(
    process.env.ENABLE_INTERNAL_ANALYTICS
  ),
  /** Feature flag to enable non-image media */
  enableAudio: true,
}
