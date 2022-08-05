module.exports = {
  extends: ['../../.eslintrc.js'],
  env: { jest: true },
  rules: {
    'import/no-named-as-default-member': ['off'],
    '@intlify/vue-i18n/no-raw-text': ['off'],
    'no-restricted-imports': [
      'error',
      {
        name: 'pinia',
        message:
          'Please import pinia test utils from `~~/test/unit/test-utils/pinia`. The test-utils version ensures proper setup of universally necessary Nuxt context mocks.',
      },
    ],
  },
}
