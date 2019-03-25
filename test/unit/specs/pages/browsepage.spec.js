import BrowsePage from '@/pages/BrowsePage';
import render from '../../test-utils/render';

describe('BrowsePage', () => {
  it('should render correct contents', () => {
    const wrapper = render(BrowsePage);
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
    expect(wrapper.find('.browse-page').element).toBeDefined();
  });
});
