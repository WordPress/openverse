import type { Preview } from "@storybook/vue3"

const preview: Preview = {
  parameters: {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
    locale: {
      name: "Locale",
      description: "I18n "
    }
  },
}

export default preview
