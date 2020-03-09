
import PhotoDetailPage from '@/pages/server/PhotoDetailPage';
import render from '../../../test-utils/render';

describe('PhotoDetailPage', () => {
  const options = {
    propsData: {
      query: {
        provider: 'foo',
      },
    },
    mocks: {
      $store: {
        state: {
          query: {
            q: 'foo',
            provider: 'foo',
          },
          image: {
            id: 1,
          },
        },
        dispatch: jest.fn(),
      },
    },
  };
  it('should render correct contents', () => {
    const wrapper = render(PhotoDetailPage, options);

    expect(wrapper.find('.browse-page'));
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'photo-details' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'photo-tags' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });
});
