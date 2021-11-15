import BrowsePage from '~/pages/search'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

describe('Search Grid Wrapper', () => {
  let options
  let localVue
  let storeMock
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          state: {
            query: { q: 'foo' },
            isFilterVisible: false,
          },
          mutations: {
            SET_FILTER_IS_VISIBLE: jest.fn(),
          },
        },
      },
    })
    options = {
      localVue,
      store: storeMock,
      stubs: {
        AppModal: true,
        FilterDisplay: true,
        NuxtChild: true,
        ScrollButton: true,
        SearchGridFilter: true,
        SearchGridForm: true,
        SearchTypeTabs: true,
        SearchGridManualLoad: true,
      },
      mocks: {
        $router: { path: { name: 'search-image' } },
        $route: { path: '/search/image' },
      },
    }
  })
  it('renders correct content', () => {
    const wrapper = render(BrowsePage, options)
    expect(wrapper.find('[data-testid="scroll-button"]').element).toBeDefined()
    window.scrollY = 50
    wrapper.vm.checkScrollLength()
    expect(wrapper.vm.showScrollButton).toBe(false)
  })

  it('renders the scroll button when the page scrolls down', () => {
    const wrapper = render(BrowsePage, options)
    window.scrollY = 80
    wrapper.vm.checkScrollLength()
    expect(wrapper.vm.showScrollButton).toBe(true)
  })
})
