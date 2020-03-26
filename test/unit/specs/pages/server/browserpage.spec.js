
import BrowsePage from '@/pages/server/BrowsePage';
import render from '../../../test-utils/render';

describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const wrapper = render(BrowsePage);

    expect(wrapper.find('.browse-page'));
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'search-grid-form' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });
});
