import { STAGING } from "#shared/constants/deploy-env"

import type { PlaywrightTestConfig } from "@playwright/test"

const UPDATE_TAPES = process.env.UPDATE_TAPES || "false"

export const API_URL = "http://localhost:49153/"

/**
 * Enabling `FASTSTART` allows you to bypass running the nuxt build
 * when rapidly debugging tests locally within the container. If you
 * already have the Docker image, this is an easy way to iterate on
 * tests and do log-based debugging without needing to download the
 * enormous browser binaries (on top of the already huge Docker image
 * download).
 *
 * Note that visual-regression tests can be quite flaky when using
 * `FASTSTART`.
 */
const pwCommand = process.env.FASTSTART !== "false" ? "dev" : "prod:playwright"

const localBaseURL = "http://localhost:8443"
const baseURL = process.env.PLAYWRIGHT_BASE_URL || localBaseURL

// Only run the local webserver if the baseURL is the local
// In other words, don't bother running the webserver if the test target is a live environment
const webServer =
  baseURL === localBaseURL
    ? {
        command: `pnpm exec npm-run-all -p -r talkback ${pwCommand}`,
        timeout: process.env.CI ? 60_000 * 5 : 60_000 * 10, // 5 minutes in CI, 10 in other envs
        port: 8443,
        reuseExistingServer: !process.env.CI || process.env.PWDEBUG === "1",
        env: {
          UPDATE_TAPES: UPDATE_TAPES,
          NUXT_PUBLIC_API_URL: API_URL,
          // Must be true for seo tests to receive appropriate values
          NUXT_PUBLIC_SITE_INDEXABLE: "true",
          NUXT_PUBLIC_DEPLOYMENT_ENV: STAGING,
          NUXT_PUBLIC_PLAUSIBLE_DOMAIN: "localhost",
          NUXT_PUBLIC_PLAUSIBLE_API_HOST: "http://localhost:50290",
          NUXT_PUBLIC_PLAUSIBLE_AUTO_PAGEVIEWS: "false",
          NUXT_PUBLIC_PLAUSIBLE_IGNORED_HOSTNAMES: "[]",
          // Necessary for i18n tests
          NUXT_PUBLIC_I18N_BASE_URL: "https://openverse.org",
        },
      }
    : undefined

const config: PlaywrightTestConfig = {
  forbidOnly: !!process.env.CI,
  webServer,
  use: {
    baseURL,
    trace: "retain-on-failure",
  },
  timeout: 8 * 1e3, // 8 seconds in enough to see if the test is stuck
  /**
   * When updating or recreating tapes, if we have more than one worker running
   * then Talkback is liable to see multiple requests at the same time that would
   * otherwise all match the same tape. Because the requests come in all at once
   * there isn't time for Talkback to have written the tape for one of the requests
   * and then reuse it for the others. If we run with a single worker when updating
   * tapes then we can avoid this problem. Defaulting to `undefined` means the
   * Playwright default of using 1/2 of the number of CPU cores continues to work otherwise.
   *
   * Also: when running Playwright against a live environment, only use a single worker
   * to avoid the test also becoming a load test.
   */
  workers: UPDATE_TAPES === "true" || baseURL !== localBaseURL ? 1 : undefined,
  expect: {
    toMatchSnapshot: {
      threshold: 0.1,
    },
  },
}

export default config
