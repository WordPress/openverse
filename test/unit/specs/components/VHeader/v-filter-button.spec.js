import { render, screen } from '@testing-library/vue'

import VFilterButton from '~/components/VHeader/VFilterButton.vue'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import messages from '../../../../../src/locales/en.json'
import { ref } from '@nuxtjs/composition-api'

describe('VFilterButton', () => {
  let options = {}
  let storeMock
  let localVue
  let appliedFilters = []
  let props = {}
  let provided = {
    isMinScreenMd: ref(true),
    isHeaderScrolled: ref(false),
  }

  const i18n = new VueI18n({
    locale: 'en',
    localeProperties: { dir: 'ltr' },
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
      mocks: { $nuxt: { context: { store: storeMock, i18n } } },
      provide: provided,
    }
  })

  describe('Above the medium breakpoint', () => {
    it('always shows the label and icon', () => {
      provided.isMinScreenMd.value = true
      const { container } = render(VFilterButton, options)

      const button = screen.getByText('Filters')
      const icon = container.querySelector('svg')

      expect(button).toBeVisible()
      expect(icon).toBeVisible()
    })
    it('shows the count and text when filters are applied', () => {
      provided.isMinScreenMd.value = true
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      render(VFilterButton, options)

      const button = screen.getByText(`${filterCount} Filters`)

      expect(button).toBeVisible()
    })
    it('does not show the icon when filters are applied', () => {
      provided.isMinScreenMd.value = true
      appliedFilters = ['mockfilter1', 'mockfilter2']

      const { container } = render(VFilterButton, options)
      const icon = container.querySelector('svg')

      expect(icon).not.toBeVisible()
    })
  })

  describe('below the medium breakpoint', () => {
    it('only shows the filter icon by default', () => {
      provided.isMinScreenMd.value = false
      appliedFilters = []
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const label = screen.queryByTestId('filterbutton-label')

      expect(icon).toBeVisible()
      expect(label).not.toBeVisible()
    })
    it('only shows the count and label when filters are applied', () => {
      provided.isMinScreenMd.value = false
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const button = screen.getByText(`${filterCount} Filters`)

      expect(icon).not.toBeVisible()
      expect(button).toBeVisible()
    })
    it('only shows the count when filters are applied and the user scrolls', () => {
      provided.isMinScreenMd.value = false
      provided.isHeaderScrolled.value = true
      // +2 to guarantee it's plural
      const filterCount = Math.floor(Math.random() * 10) + 2
      appliedFilters = Array(filterCount).fill('')
      const { container } = render(VFilterButton, options)

      const icon = container.querySelector('svg')
      const button = screen.getByText(filterCount)

      expect(icon).not.toBeVisible()
      expect(button).toBeVisible()
    })
  })
})
