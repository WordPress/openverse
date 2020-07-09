import CollectionBrowsePage from '@/pages/CollectionBrowsePage';
import render from '../../test-utils/render';

describe('CollectionBrowsePage', () => {
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
        },
        dispatch: jest.fn(),
      },
    },
  };

  it('should render correct contents', () => {
    const wrapper = render(CollectionBrowsePage);
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });

  it('should dispatch FETCH_COLLECTION_IMAGES', () => {
    const params = { foo: 'bar' };
    const wrapper = render(CollectionBrowsePage, options);
    wrapper.vm.getImages(params);
    expect(options.mocks.$store.dispatch).toHaveBeenCalledWith('FETCH_COLLECTION_IMAGES', params);
  });
});
