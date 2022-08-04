module.exports = {
  extends: ['../../.eslintrc.js'],
  env: { jest: true },
  rules: {
    'import/no-named-as-default-member': ['off'],
    '@intlify/vue-i18n/no-raw-text': ['off'],
  },
}
