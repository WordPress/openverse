module.exports = {
  extends: '../../.eslintrc.js',
  rules: {
    'unicorn/filename-case': [
      'error',
      // Allow things like `Component.stories.js` and `Component.types.js`
      {
        case: 'pascalCase',
        ignore: ['.eslintrc.js', '.*\\..*\\.js'],
      },
    ],
  },
}
