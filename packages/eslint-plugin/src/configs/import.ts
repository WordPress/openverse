export = {
  extends: ["plugin:import/recommended"],
  plugins: ["import"],
  rules: {
    "import/no-unresolved": [
      "error",
      {
        // https://github.com/nuxt-community/svg-module/issues/4
        ignore: [".svg"],
      },
    ],
    "import/newline-after-import": ["error"],
    "import/order": [
      "error",
      {
        "newlines-between": "always-and-inside-groups",
        groups: [
          "builtin",
          "external",
          "internal",
          "parent",
          "sibling",
          "index",
          "object",
          "type",
        ],
        pathGroups: [
          {
            // Treat vue and composition-api as "builtin"
            pattern: "(vue|@nuxtjs/composition-api)",
            group: "builtin",
            position: "before",
          },
          {
            // Move assets to the very end of the imports list
            pattern: "~/assets/**",
            group: "type",
            position: "after",
          },
          {
            // Treat components as their own group and move to the end of the internal imports list
            pattern: "~/components/**",
            group: "internal",
            position: "after",
          },
          /**
           * These next two must come after any more specific matchers
           * as the plugin uses the patterns in order and does not sort
           * multiple-matches by specificity, it just takes the _first_
           * pattern that matches and applies that group to the import.
           */
          {
            // Document webpack alias
            pattern: "~/**",
            group: "internal",
            position: "before",
          },
          {
            // Document webpack alias
            pattern: "~~/**",
            group: "external",
            position: "after",
          },
        ],
      },
    ],
    "import/extensions": ["error", "always", { js: "never", ts: "never" }],
  },
}
