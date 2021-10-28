import BrowsePage from '~/pages/search'
import render from '../../test-utils/render'

const options = {
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
    $store: {
      commit: jest.fn(),
      state: { query: { q: 'foo' }, isFilterVisible: false },
    },
    $router: { path: { name: 'search-image' } },
    $route: { path: '/search/image' },
  },
}

describe('Search Grid Wrapper', () => {
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
