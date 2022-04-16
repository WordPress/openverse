/**
 * `.nuxt-storybook` doesn't exist in the CI when it
 * lints files unless we ran the storybook build before linting,
 * meaning that the imports used in the modules in this directory
 * are mostly unavailable.
 *
 * To avoid turning these rules off we'd have to run the storybook
 * build in CI before linting (or even instruct people to run
 * storybook build locally before trying to lint) and that's just too
 * heavy a lift when we can instead disable the rules for just this
 * directory.
 */
module.exports = {
  extends: '../.eslintrc.js',
  rules: {
    'import/extensions': 'off',
    'import/export': 'off',
    'import/no-unresolved': 'off',
  },
}
