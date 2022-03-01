/**
 * Regarding the various eslint-disables in this file,
 * `.nuxt-storybook` doesn't exist in the CI when it
 * lints files unless we ran the storybook build before linting.
 *
 * That would significantly increase the time it takes for the
 * lint job to run, so it's nice to avoid that.
 */

// eslint-disable-next-line import/export, import/no-unresolved
export * from '~~/.nuxt-storybook/storybook/preview.js'
import {
  globalTypes as nuxtGlobalTypes,
  decorators as nuxtDecorators,
  // eslint-disable-next-line import/no-unresolved
} from '~~/.nuxt-storybook/storybook/preview.js'

// eslint-disable-next-line import/order
import { WithRTL } from './decorators/with-rtl'

// eslint-disable-next-line import/export
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

// eslint-disable-next-line import/export
export const decorators = [...nuxtDecorators, WithRTL]
