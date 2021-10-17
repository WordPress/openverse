module.exports = {
  env: {
    node: true,
  },
  extends: ['eslint:recommended', 'plugin:prettier/recommended'],
  parserOptions: {
    ecmaVersion: 12,
  },
  plugins: [],
  rules: {
    semi: [2, 'never'],
    'no-console': 'off',
  },
}
