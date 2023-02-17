/* eslint-disable import/order */

export * from "~~/.nuxt-storybook/storybook/preview"
import {
  globalTypes as nuxtGlobalTypes,
  decorators as nuxtDecorators,
} from "~~/.nuxt-storybook/storybook/preview"

import { WithRTL } from "./decorators/with-rtl"
import { WithUiStore } from "./decorators/with-ui-store"

/* eslint-enable import/order */

export const globalTypes = {
  ...nuxtGlobalTypes,
  languageDirection: {
    name: "RTL",
    description: "Simulate an RTL language.",
    defaultValue: "ltr",
    toolbar: {
      icon: "globe",
      items: [
        { value: "ltr", title: "LTR" },
        { value: "rtl", title: "RTL" },
      ],
    },
  },
}

export const decorators = [...nuxtDecorators, WithRTL, WithUiStore]
