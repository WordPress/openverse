import type { TSESLint } from "@typescript-eslint/utils"

export = {
  extends: [
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "plugin:@intlify/vue-i18n/recommended",
  ],
  plugins: ["vue", "vuejs-accessibility", "@intlify/vue-i18n"],
  rules: {
    // Vue i18n rules
    "@intlify/vue-i18n/no-deprecated-i18n-component": "error",
    "@intlify/vue-i18n/no-i18n-t-path-prop": "error",
    "@intlify/vue-i18n/key-format-style": [
      "error",
      "camelCase",
      {
        allowArray: false,
        splitByDots: false,
      },
    ],
    // Vue rules
    "vue/block-order": [
      "error",
      {
        order: ["script[setup]", "script:not([setup])", "template", "style"],
      },
    ],
    "vue/padding-line-between-blocks": ["error", "always"],
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
      { registeredComponentsOnly: false, ignores: ["i18n", "i18n-t"] },
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

    "@intlify/vue-i18n/no-raw-text": [
      "error",
      {
        ignoreText: [
          // Brand names that should not be translated
          "Common Crawl",
          "Creative Commons",
          "Europeana",
          "Europeana API",
          "Smithsonian Institute",
          "Flickr",
          "Openverse",
          "WordPress",
          "GitHub",

          // Domains and emails
          "openverse@wordpress.org",
          "oldsearch.creativecommons.org",
          "Openverse.org",
        ],
      },
    ],
  },
  overrides: [
    {
      files: ["frontend/src/pages/**/*.vue", "frontend/src/error.vue"],
      rules: { "vue/multi-word-component-names": "off" },
    },
  ],
} satisfies TSESLint.Linter.Config
