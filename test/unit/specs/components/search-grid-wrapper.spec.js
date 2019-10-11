import SearchGrid from '@/components/SearchGrid';
import render from '../../test-utils/render';

describe('Search Grid Wrapper', () => {
  it('renders correct content', () => {
    const wrapper = render(SearchGrid);
    expect(wrapper.find({ name: 'search-grid-manual-load' })).toBeDefined();
    expect(wrapper.find({ name: 'scroll-button' })).toBeDefined();
  });

  it('renders the scroll button when the page scrolls down', () => {
    const wrapper = render(SearchGrid);
    window.scrollY = 80;
    wrapper.vm.checkScrollLength();
    expect(wrapper.vm.showScrollButton).toBe(true);
  });
});
