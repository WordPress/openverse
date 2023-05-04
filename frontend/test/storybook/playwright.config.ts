import path from "path"

import { addAliases } from "module-alias"

import type { PlaywrightTestConfig } from "@playwright/test"

addAliases({
  "~": path.resolve(process.cwd(), "src"),
  "~~": process.cwd(),
})

const config: PlaywrightTestConfig = {
  webServer: {
    command: "pnpm storybook",
    timeout: 60_000 * 5, // 5 minutes
    url: "http://localhost:54000/iframe.html?id=introduction-openverse-ui--page",
    reuseExistingServer: !process.env.CI || process.env.PWDEBUG === "1",
  },
  storybook: {
    port: 6006, // standard port for Storybook
    stories: ["~/**/*.stories.@(mdx|js)"],
    addons: [
      {
        name: "@storybook/addon-essentials",
        options: {
          backgrounds: true,
          viewport: true,
          toolbars: true,
        },
      },
    ],
    parameters: {
      backgrounds: {
        default: "White",
        values: [
          { name: "White", value: "#ffffff" },
          { name: "Dark charcoal", value: "#30272e" },
        ],
      },
      options: {
        storySort: {
          order: ["Introduction", ["Openverse UI"], "Meta"],
        },
      },
      viewport: {
        viewports: VIEWPORTS,
      },
    },
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
