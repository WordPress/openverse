import { defineConfig } from "@playwright/test"

export default defineConfig({
  forbidOnly: !!process.env.CI,
  webServer: {
    command: "pnpm prod:storybook",
    timeout: 60_000 * 5, // 5 minutes
    url: "http://localhost:54000/iframe.html?id=introduction-openverse-ui--page",
    reuseExistingServer: !process.env.CI || process.env.PWDEBUG === "1",
  },
  use: {
    baseURL: "http://localhost:54000",
    trace: "retain-on-failure",
  },
  timeout: 5 * 1e3, // 5 seconds in enough to see if the test is stuck
  expect: {
    toMatchSnapshot: {
      // To avoid flaky tests, we allow a small amount of pixel difference.
      maxDiffPixelRatio: 0.003,
    },
  },
})
