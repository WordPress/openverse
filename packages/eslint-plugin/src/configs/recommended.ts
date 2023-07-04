export const recommended = {
  rules: {
    "@openverse/analytics-configuration": [
      "error",
      {
        reservedPropNames: [
          "timestamp",
          "language",
          "breakpoint",
          "ua",
          "os",
          "platform",
          "browser",
          "version",
          "origin",
          "pathname",
          "referrer",
          "width",
          "height",
        ],
      },
    ],
  },
}
