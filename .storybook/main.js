const { nuxifyStorybook } = require('../.nuxt-storybook/storybook/main')

module.exports = nuxifyStorybook({
  webpackFinal(config) {
    // extend config here

    return config
  },
  stories: [
    // Add your stories here
  ],
  addons: [
    // Add your addons here
  ],
})
