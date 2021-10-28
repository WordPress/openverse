import SearchGrid from '~/components/SearchGrid'
import render from '../../test-utils/render'

const options = {
  stubs: {
    ScrollButton: true,
    SearchGridManualLoad: true,
  },
  mocks: { $store: { state: { query: { q: 'foo' } } } },
}

describe('Search Grid Wrapper', () => {
  it('renders correct content', () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.find('[data-testid="search-grid"]').element).toBeDefined()
  })
})
