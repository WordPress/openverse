import { VIEWPORTS } from "~/constants/screens"

import { WithUiStore } from "~~/.storybook/decorators/with-ui-store"
import { WithRTL } from "~~/.storybook/decorators/with-rtl"
import { WithTheme } from "~~/.storybook/decorators/with-theme"

import type { Preview } from "@storybook/vue3"

const preview: Preview = {
  decorators: [WithRTL, WithUiStore, WithTheme],
  globalTypes: {
    theme: {
      name: "Theme",
      description: "Color theme",
      table: {
        defaultValue: { summary: "light" },
      },
      toolbar: {
        icon: "circlehollow",
        items: [
          { value: "light", title: "Light" },
          { value: "dark", title: "Dark" },
        ],
      },
    },
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
  initialGlobals: {
    theme: "light",
    languageDirection: "ltr",
    backgrounds: { value: "light" },
  },
}

export default preview
