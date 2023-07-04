import type { PlaywrightTestConfig } from "@playwright/test"

const config: PlaywrightTestConfig = {
  forbidOnly: !!process.env.CI,
  webServer: {
    command: "pnpm storybook",
    timeout: 60_000 * 5, // 5 minutes
    url: "http://localhost:54000/iframe.html?id=introduction-openverse-ui--page",
    reuseExistingServer: !process.env.CI || process.env.PWDEBUG === "1",
  },
  use: {
    baseURL: "http://localhost:54000",
    trace: "retain-on-failure",
  },
  timeout: 60 * 1e3, // 1 minute
  expect: {
    toMatchSnapshot: {
      // To avoid flaky tests, we allow a small amount of pixel difference.
      maxDiffPixelRatio: 0.01,
    },
  },
}

export default config
