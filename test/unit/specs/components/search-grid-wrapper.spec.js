import SearchGrid from '~/components/SearchGrid'
import render from '../../test-utils/render'

describe('Search Grid Wrapper', () => {
  it('renders correct content', () => {
    const wrapper = render(SearchGrid)
    expect(wrapper.find('[data-testid="search-grid"]').element).toBeDefined()
    expect(wrapper.find('[data-testid="scroll-button"]').element).toBeDefined()
  })

  it('renders the scroll button when the page scrolls down', () => {
    const wrapper = render(SearchGrid)
    window.scrollY = 80
    wrapper.vm.checkScrollLength()
    expect(wrapper.vm.showScrollButton).toBe(true)
  })
})
