module.exports = {
  extends: '../../.eslintrc.js',
  rules: {
    'unicorn/filename-case': [
      'error',
      { case: 'pascalCase', ignore: ['.eslintrc.js', '.*\\.stories\\.js'] },
    ],
  },
}
