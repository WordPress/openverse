import tseslint, { configs as tsConfigs } from "typescript-eslint"
import eslintPluginVue from "eslint-plugin-vue"
import eslintPluginVueI18n from "@intlify/eslint-plugin-vue-i18n"
import pluginVueA11y from "eslint-plugin-vuejs-accessibility"
import eslint from "@eslint/js"
import { FlatConfig } from "@typescript-eslint/utils/ts-eslint"

// Filter out yaml files from vue-i18n configs
const vueI18nConfigs = eslintPluginVueI18n.configs["flat/recommended"].filter(
  (config: FlatConfig.Config) => {
    return !config.files || !config.files.includes("*.yaml")
  }
)

export default tseslint.config(
  {
    name: "openverse:vue-config",
    files: ["*.vue", "**/*.vue"],
    settings: {
      "vue-i18n": {
        localeDir: "./frontend/src/locales/*.{json}",
        messageSyntaxVersion: "^9.0.0",
      },
    },
    languageOptions: {
      parserOptions: {
        parser: "@typescript-eslint/parser",
      },
    },
    extends: [
      eslint.configs.recommended,
      ...tsConfigs.recommended,
      ...eslintPluginVue.configs["flat/recommended"],
      ...pluginVueA11y.configs["flat/recommended"],
      ...vueI18nConfigs,
    ],
    rules: {
      // Vue rules
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

      // Vue a11y rules
      "vuejs-accessibility/aria-role": "error",
      "vuejs-accessibility/label-has-for": [
        "error",
        { required: { some: ["nesting", "id"] } },
      ],

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
  },
  {
    name: "openverse:vue:multi-word-component-names",
    files: ["frontend/src/pages/**/*.vue", "frontend/src/error.vue"],
    rules: { "vue/multi-word-component-names": "off" },
  },
  {
    name: "openverse:vue:json-i18n-settings",
    settings: {
      "vue-i18n": {
        localeDir: "./frontend/src/locales/*.{json}",
        messageSyntaxVersion: "^9.0.0",
      },
    },
    files: ["**/*.json", "**/*.json5", "**/*.ts"],
  },
  {
    name: "openverse:vue:i18n-translation-strings",
    files: ["frontend/src/locales/en.json5", "frontend/test/locales/*.json"],

    extends: [...eslintPluginVueI18n.configs["flat/recommended"]],
    rules: {
      "@openverse/translation-strings": ["error"],
    },
  },
  {
    name: "openverse:case:locales-exceptions",
    files: [
      "frontend/src/locales/scripts/en.json5",
      "frontend/test/locales/*.json",
    ],
    rules: {
      "jsonc/key-name-casing": [
        "error",
        {
          camelCase: true,
          "kebab-case": false,
          snake_case: true, // for err_* keys
          ignores: ["ncSampling+", "sampling+"],
        },
      ],
    },
  },
  {
    name: "openverse:locales-quotes",
    files: ["frontend/src/locales/scripts/en.json5"],
    rules: {
      "jsonc/quote-props": "off",
      "jsonc/quotes": "off",
    },
  }
)
