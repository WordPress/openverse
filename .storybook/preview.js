export * from '~~/.nuxt-storybook/storybook/preview.js'
import {
  globalTypes as nuxtGlobalTypes,
  decorators as nuxtDecorators,
} from '~~/.nuxt-storybook/storybook/preview.js'

import { WithRTL } from './decorators/with-rtl'

export const globalTypes = {
  ...nuxtGlobalTypes,
  languageDirection: {
    name: 'RTL',
    description: 'Simulate an RTL language.',
    defaultValue: 'ltr',
    toolbar: {
      icon: 'globe',
      items: [
        { value: 'ltr', title: 'LTR' },
        { value: 'rtl', title: 'RTL' },
      ],
    },
  },
}

export const decorators = [...nuxtDecorators, WithRTL]
