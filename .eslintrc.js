module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  parserOptions: {
    parser: '@typescript-eslint/parser',
  },
  extends: [
    'plugin:@typescript-eslint/recommended',
    'eslint:recommended',
    'plugin:vue/recommended',
    'plugin:prettier/recommended',
    'plugin:vuejs-accessibility/recommended',
    'plugin:@intlify/vue-i18n/recommended',
    'plugin:import/recommended',
    'plugin:eslint-comments/recommended',
  ],
  plugins: [
    '@typescript-eslint',
    'eslint-plugin-tsdoc',
    'vue',
    'vuejs-accessibility',
    'unicorn',
  ],
  rules: {
    semi: [2, 'never'],
    'no-console': 'off',
    'vue/max-attributes-per-line': 'off',
    'vue/require-prop-types': 'off',
    'vue/require-default-prop': 'off',
    'vue/html-closing-bracket-newline': 'off',
    'vue/html-indent': 'off',
    'vue/singleline-html-element-content-newline': 'off',
    'vue/component-name-in-template-casing': [
      'error',
      'PascalCase',
      { registeredComponentsOnly: false, ignores: ['i18n'] },
    ],
    'vue/html-self-closing': [
      'error',
      {
        html: {
          void: 'always',
          normal: 'always',
          component: 'always',
        },
        svg: 'always',
        math: 'always',
      },
    ],
    'vuejs-accessibility/aria-role': 'warn',
    'vuejs-accessibility/label-has-for': [
      'warn',
      { required: { some: ['nesting', 'id'] } },
    ],
    /**
     * Custom rule to disallow raw `<a></a>` tag usage.
     * Learn more about vue-eslint-parser's AST syntax:
     * https://github.com/vuejs/vue-eslint-parser/blob/master/docs/ast.md
     */
    'vue/no-restricted-syntax': [
      'error',
      {
        selector: 'VElement[name="a"]',
        message: 'Use the <VLink> component instead of a raw <a> tag.',
      },
      {
        selector: 'VElement[name="nuxtlink"]',
        message: 'Use the <VLink> component instead of <NuxtLink>.',
      },
      {
        selector: 'VElement[name="routerlink"]',
        message: 'Use the <VLink> component instead of <RouterLink>.',
      },
    ],
    'unicorn/filename-case': ['error', { case: 'kebabCase' }],
    '@typescript-eslint/ban-ts-comment': ['warn'],
    '@typescript-eslint/no-var-requires': ['off'],
    'import/no-unresolved': [
      'error',
      {
        // https://github.com/nuxt-community/svg-module/issues/4
        ignore: ['.svg'],
      },
    ],
    'import/newline-after-import': ['error'],
    'import/order': [
      'error',
      {
        'newlines-between': 'always-and-inside-groups',
        groups: [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index',
          'object',
          'type',
        ],
        pathGroups: [
          {
            // Treate vue and composition-api as "builtin"
            pattern: '(vue|@nuxtjs/composition-api)',
            group: 'builtin',
            position: 'before',
          },
          {
            // Move assets to the very end of the imports list
            pattern: '~/assets/**',
            group: 'type',
            position: 'after',
          },
          {
            // Treat components as their own group and move to the end of the internal imports list
            pattern: '~/components/**',
            group: 'internal',
            position: 'after',
          },
          /**
           * These next two must come after any more specific matchers
           * as the plugin uses the patterns in order and does not sort
           * multiple-matches by specificity, it just takes the _first_
           * pattern that matches and applies that group to the import.
           */
          {
            // Document webpack alias
            pattern: '~/**',
            group: 'internal',
            position: 'before',
          },
          {
            // Document webpack alias
            pattern: '~~/**',
            group: 'external',
            position: 'after',
          },
        ],
      },
    ],
  },
  overrides: [
    {
      files: ['*.ts'],
      rules: {
        'tsdoc/syntax': 'warn',
      },
    },
  ],
  settings: {
    'vue-i18n': {
      localeDir: './src/locales/*.{json}',
      messageSyntaxVersion: '^8.24.3',
    },
    'import/resolver': {
      'eslint-import-resolver-custom-alias': {
        alias: {
          '~': './src',
          '~~': '.',
        },
        /**
         * SVG imports are excluded for the import/no-unresolved
         * rule above due to due to lack of support for `?inline` suffix
         *
         * Therefore, there's no need to configure them here
         */
        extensions: ['.js', '.ts', '.vue', '.png'],
      },
    },
  },
}
