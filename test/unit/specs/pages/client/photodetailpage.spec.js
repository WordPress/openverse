import PhotoDetailPage from '@/pages/client/PhotoDetailPage';
import render from '../../../test-utils/render';

describe('PhotoDetailPage', () => {
  it('should render correct contents', () => {
    const wrapper = render(PhotoDetailPage);

    expect(wrapper.find('.browse-page'));
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'photo-details' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'photo-tags' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'related-images' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });
});
