import { render, screen } from '@testing-library/vue'

import VFilterButton from '~/components/VHeader/VFilterButton.vue'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import messages from '../../../../../src/locales/en.json'
import { isMinScreen } from '~/composables/use-media-query'

/**
 * For some reason I need to mock the implementation
 * of this mock in each test, or it doesn't work.
 *
 * In each implementation I'm faking returning a ref
 * with `mockImplementation(() => ({value: true}))`
 * that may be related.
 */
jest.mock('~/composables/use-media-query', () => ({
  isMinScreen: jest.fn(),
}))

describe('VFilterButton', () => {
  let options = {}
  let storeMock
  let localVue
  let appliedFilters = []
  let props = {}

  const i18n = new VueI18n({
    locale: 'en',
    localeProperties: {
      dir: 'ltr',
    },
    fallbackLocale: 'en',
    messages: { en: messages },
  })
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(VueI18n)

    storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          getters: {
            isAnyFilterApplied: () => appliedFilters.length > 0,
            appliedFilterTags: () => appliedFilters,
          },
        },
      },
    })
    options = {
      localVue,
      propsData: props,
      mocks: {
        $nuxt: {
          context: {
            store: storeMock,
            i18n,
          },
        },
      },
    }
  })

  describe('Above the medium breakpoint', () => {
    it('always shows the label and icon', () => {
      isMinScreen.mockImplementation(() => ({ value: true }))
      const { container } = render(VFilterButton, options)

      const button = screen.getByText('Filters')
      const icon = container.querySelector('svg')

      expect(button).toBeVisible()
      expect(icon).toBeVisible()
    })
    it('shows the count and text when filters are applied', () => {
      isMinScreen.mockImplementation(() => ({ value: true }))
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      render(VFilterButton, options)

      const button = screen.getByText(`${filterCount} Filters`)

      expect(button).toBeVisible()
    })
    it('does not show the icon when filters are applied', () => {
      isMinScreen.mockImplementation(() => ({ value: true }))
      appliedFilters = ['mockfilter1', 'mockfilter2']

      const { container } = render(VFilterButton, options)
      const icon = container.querySelector('svg')

      expect(icon).not.toBeInTheDocument()
    })
  })

  describe('below the medium breakpoint', () => {
    it('only shows the filter icon by default', () => {
      isMinScreen.mockImplementation(() => ({ value: false }))
      appliedFilters = []
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const label = screen.queryByTestId('filterbutton-label')

      expect(icon).toBeVisible()
      expect(label).not.toBeInTheDocument()
    })
    it('only shows the count and label when filters are applied', () => {
      isMinScreen.mockImplementation(() => ({ value: false }))
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const button = screen.getByText(`${filterCount} Filters`)

      expect(icon).not.toBeInTheDocument()
      expect(button).toBeVisible()
    })
    it('only shows the count when filters are applied and the user scrolls', () => {
      isMinScreen.mockImplementation(() => ({ value: false }))
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      props.isHeaderScrolled = true
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const button = screen.getByText(filterCount)

      expect(icon).not.toBeInTheDocument()
      expect(button).toBeVisible()
    })
  })
})
