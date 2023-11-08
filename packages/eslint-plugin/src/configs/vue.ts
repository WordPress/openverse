import type { TSESLint } from "@typescript-eslint/utils"

const i18nDestructureRules = ["t", "tc", "te", "td", "d", "n"].map(
  (methodName) => ({
    selector: `VariableDeclarator[id.type="ObjectPattern"]:has(Property[key.name="${methodName}"])[init.callee.name="useI18n"]`,
    message: `Do not destructure ${methodName} from the i18n object as its methods internally depend on "this". Instead, use it directly (e.g., "i18n.${methodName}"). If you need an independent reference to the function then bind it or wrap it in a closure.`,
  })
)

export = {
  extends: [
    "plugin:vue/recommended",
    "plugin:vue/vue3-recommended",
    "plugin:vuejs-accessibility/recommended",
    "plugin:@intlify/vue-i18n/recommended",
  ],
  plugins: ["vue", "vuejs-accessibility", "@intlify/vue-i18n"],
  rules: {
    // Enable these rules after the Nuxt 3 migration
    "vue/no-deprecated-dollar-listeners-api": "off",
    "vue/no-v-for-template-key-on-child": "off",
    "vue/no-deprecated-v-on-native-modifier": "off",
    // TODO: enable after https://github.com/WordPress/openverse/issues/3268 is fixed
    "vue/no-deprecated-props-default-this": "off",

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
} satisfies TSESLint.Linter.Config
