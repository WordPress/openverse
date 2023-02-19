module.exports = {
  root: true,
  env: {
    node: true,
    es6: true,
  },
  parserOptions: {
    ecmaVersion: 'latest',
  },
  extends: ['eslint:recommended', 'prettier'],
  rules: {
    semi: [2, 'never'],
    'no-console': 'off',
  },
}
