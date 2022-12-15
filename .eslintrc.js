// WebStorm fix for `~` alias not working:
// https://intellij-support.jetbrains.com/hc/en-us/community/posts/115000771544-ESLint-does-not-work-with-webpack-import-resolver-in-2017-3
process.chdir(__dirname)

const i18nDestructureRules = ["t", "tc", "te", "td", "d", "n"].map(
  (methodName) => ({
    selector: `VariableDeclarator[id.type="ObjectPattern"]:has(Property[key.name="${methodName}"])[init.callee.name="useI18n"]`,
    message: `Do not destructure ${methodName} from the i18n object as its methods internally depend on "this". Instead, use it directly (e.g., "i18n.${methodName}"). If you need an independent reference to the function then bind it or wrap it in a closure.`,
  })
)

module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  parserOptions: {
    parser: "@typescript-eslint/parser",
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/recommended",
    "plugin:prettier/recommended",
    "plugin:vuejs-accessibility/recommended",
    "plugin:@intlify/vue-i18n/recommended",
    "plugin:import/recommended",
    "plugin:eslint-comments/recommended",
  ],
  plugins: [
    "@typescript-eslint",
    "eslint-plugin-tsdoc",
    "vue",
    "vuejs-accessibility",
    "unicorn",
  ],
  rules: {
    semi: [2, "never"],
    "no-console": "off",
    "prettier/prettier": "off",
    "vue/max-attributes-per-line": "off",
    "vue/require-prop-types": "off",
    "vue/require-default-prop": "off",
    "vue/html-closing-bracket-newline": "off",
    "vue/html-indent": "off",
    "vue/singleline-html-element-content-newline": "off",
    "vue/block-lang": [
      "error",
      {
        // This confusing naming prevents the use of 'lang' directives
        // entirely on Vue SFC style blocks.
        style: { allowNoLang: true },
      },
    ],
    "vue/component-name-in-template-casing": [
      "error",
      "PascalCase",
      { registeredComponentsOnly: false, ignores: ["i18n"] },
    ],
    "vue/html-self-closing": [
      "error",
      {
        html: {
          void: "always",
          normal: "always",
          component: "always",
        },
        svg: "always",
        math: "always",
      },
    ],
    "vuejs-accessibility/aria-role": "error",
    "vuejs-accessibility/label-has-for": [
      "error",
      { required: { some: ["nesting", "id"] } },
    ],
    /**
     * Custom rule to disallow raw `<a></a>` tag usage.
     * Learn more about vue-eslint-parser's AST syntax:
     * https://github.com/vuejs/vue-eslint-parser/blob/master/docs/ast.md
     */
    "vue/no-restricted-syntax": [
      "error",
      {
        selector: 'VElement[name="a"]',
        message: "Use the <VLink> component instead of a raw <a> tag.",
      },
      {
        selector: 'VElement[name="nuxtlink"]',
        message: "Use the <VLink> component instead of <NuxtLink>.",
      },
      {
        selector: 'VElement[name="routerlink"]',
        message: "Use the <VLink> component instead of <RouterLink>.",
      },
    ],
    "no-restricted-syntax": ["error", ...i18nDestructureRules],
    "unicorn/filename-case": ["error", { case: "kebabCase" }],
    "@typescript-eslint/no-var-requires": ["off"],
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
    "@intlify/vue-i18n/no-raw-text": [
      "error",
      {
        ignoreText: [
          // Brand names that should not be translated
          "Common Crawl",
          "Creative Commons",
          "Europeana",
          "Flickr",
          "Openverse",
          "WordPress",
          "openverse@wordpress.org",
        ],
      },
    ],
  },
  overrides: [
    {
      files: ["*.ts"],
      rules: {
        "tsdoc/syntax": "error",
      },
    },
    {
      files: ["*.spec.js"],
      rules: {
        "@intlify/vue-i18n/no-raw-text": ["off"],
      },
    },
  ],
  settings: {
    "vue-i18n": {
      localeDir: "./src/locales/*.{json}",
      messageSyntaxVersion: "^8.24.3",
    },
    "import/resolver": {
      "eslint-import-resolver-custom-alias": {
        alias: {
          "~": "./src",
          "~~": ".",
        },
        /**
         * SVG imports are excluded for the import/no-unresolved
         * rule above due to lack of support for `?inline` suffix
         *
         * Therefore, there's no need to configure them here
         */
        extensions: [".js", ".ts", ".vue", ".png"],
      },
    },
  },
}
