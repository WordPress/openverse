export = {
  plugins: ["@openverse"],
  rules: {
    "@openverse/analytics-configuration": [
      "error",
      {
        reservedPropNames: ["width", "height"],
      },
    ],
    "@openverse/no-unexplained-disabled-test": ["error"],
  },
}
