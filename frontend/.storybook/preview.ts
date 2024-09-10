import { VIEWPORTS } from "~/constants/screens"

import { WithUiStore } from "~~/.storybook/decorators/with-ui-store"
import { WithRTL } from "~~/.storybook/decorators/with-rtl"

import type { Preview } from "@storybook/vue3"

const preview: Preview = {
  decorators: [WithRTL, WithUiStore],
  globalTypes: {
    languageDirection: {
      name: "RTL",
      description: "Simulate an RTL language.",
      table: {
        defaultValue: { summary: "ltr" },
      },
      toolbar: {
        icon: "globe",
        items: [
          { value: "ltr", title: "LTR" },
          { value: "rtl", title: "RTL" },
        ],
      },
    },
  },
  parameters: {
    backgrounds: {
      default: "light",
      values: [
        { name: "light", value: "#ffffff" },
        { name: "dark", value: "#0d0d0d" },
      ],
    },
    viewport: {
      viewports: { ...VIEWPORTS },
    },
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/,
      },
    },
  },
}

export default preview
