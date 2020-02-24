
import CollectionBrowsePage from '@/pages/server/CollectionBrowsePage';
import render from '../../../test-utils/render';

describe('CollectionBrowsePage', () => {
  it('should render correct contents', () => {
    const wrapper = render(CollectionBrowsePage);

    expect(wrapper.find('.browse-page'));
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'search-grid-filter' }).vm).toBeUndefined();
    expect(wrapper.find({ name: 'search-grid-form' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });
});
