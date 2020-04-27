import ClientBrowsePage from '@/pages/client/BrowsePage';
import ServerBrowsePage from '@/pages/server/BrowsePage';
import render from '../../test-utils/render';

describe('BrowsePage', () => {
  it('should render correct client contents', () => {
    const wrapper = render(ClientBrowsePage);
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'filter-display' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'search-grid' }).vm).toBeDefined();
  });

  it('server page does not render search grid', () => {
    const wrapper = render(ServerBrowsePage);
    expect(wrapper.find({ name: 'search-grid' }).vm).toBeUndefined();
  });
});
