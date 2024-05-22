const apiUrl = process.env.API_URL ?? "https://api.openverse.org/"

/**
 * Default environment variables are set on this key. Defaults are fallbacks to existing env vars.
 * All boolean values should be designed to be false by default.
 * providerUpdateFrequency - how often we should re-fetch provider statistics.
 */
export const env = {
  apiUrl: apiUrl.endsWith("/") ? apiUrl : `${apiUrl}/`,
  filterStorageKey: "openverse-filter-visibility",
  savedSearchCount: "4",
} as const
