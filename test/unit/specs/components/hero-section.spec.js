import { fireEvent, render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import clonedeep from 'lodash.clonedeep'
import VueI18n from 'vue-i18n'
import messages from '~/locales/en.json'
import searchStore, { filterData } from '~/store/search'
import { IMAGE } from '~/constants/media'
import HeroSection from '~/components/HeroSection'
import VCheckbox from '~/components/VCheckbox'

const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: messages },
})

describe('HeroSection', () => {
  let options = {}
  let localVue
  let storeMock
  let filters
  const routerMock = { push: jest.fn() }

  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(VueI18n)
    localVue.use(Vuex)
    localVue.component('VCheckbox', VCheckbox)
    filters = clonedeep(filterData)
    storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          ...searchStore,
          state: {
            query: {
              q: 'me',
              mediaType: IMAGE,
            },
            isFilterVisible: true,
            filters,
          },
        },
      },
    })
    options = {
      mocks: {
        $router: routerMock,
        $store: storeMock,
      },
      i18n,
    }
  })
  it('should render correct contents', () => {
    render(HeroSection, options)
    screen.getByRole('search')
  })

  it('should search when a query is entered', async () => {
    render(HeroSection, options)

    const searchBox = screen.getByRole('searchbox')
    await fireEvent.update(searchBox, 'me')
    await fireEvent.click(screen.queryByTitle('Search'))

    expect(routerMock.push).toHaveBeenCalledWith({
      path: '/search/image',
      query: { q: 'me' },
    })
  })
})
