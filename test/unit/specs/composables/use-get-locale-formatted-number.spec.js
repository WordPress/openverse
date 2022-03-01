import Vue from 'vue'
import { render } from '@testing-library/vue'
import VueI18n from 'vue-i18n'

import messages from '~/locales/en.json'
import { useGetLocaleFormattedNumber } from '~/composables/use-get-locale-formatted-number'

const TestWrapper = Vue.component('TestWrapper', {
  props: ['n'],
  setup() {
    const getLocaleFormattedNumber = useGetLocaleFormattedNumber()

    return { getLocaleFormattedNumber }
  },
  template: `<div>{{ getLocaleFormattedNumber(n) }}</div>`,
})

describe('use-get-locale-formatted-number', () => {
  const getMockedI18n = (locale) => ({
    $nuxt: {
      context: {
        i18n: new VueI18n({
          locale,
          fallbackLocale: 'en',
          messages: { en: messages },
        }),
      },
    },
  })

  it.each(['ar', 'fa', 'ckb', 'ps'])(
    'should use en formatting for locales like %s that use Eastern Arabic Numerals',
    (locale) => {
      const { container } = render(TestWrapper, {
        mocks: getMockedI18n(locale),
        props: { n: 1000.01 },
      })

      expect(container.firstChild.textContent).toEqual(
        (1000.01).toLocaleString('en')
      )
      expect(container.firstChild.textContent).not.toEqual(
        (1000.01).toLocaleString(locale)
      )
    }
  )

  it.each(['pt-br', 'en-us', 'en-gb', 'ru'])(
    'should use the default formatting for locales not matching eastern arabic numeral locales like %s',
    (locale) => {
      const { container } = render(TestWrapper, {
        mocks: getMockedI18n(locale),
        props: { n: 1000.01 },
      })

      expect(container.firstChild.textContent).toEqual(
        (1000.01).toLocaleString(locale)
      )
    }
  )
})
