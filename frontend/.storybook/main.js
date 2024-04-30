const { nuxifyStorybook } = require("../.nuxt-storybook/storybook/main")

const storybook = nuxifyStorybook({
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

const generatedIconsStory = storybook.stories.indexOf(
  "@nuxtjs/svg-sprite/stories/*.stories.js"
)
storybook.stories[generatedIconsStory] =
  "../node_modules/@nuxtjs/svg-sprite/stories/*.stories.js"

module.exports = storybook
