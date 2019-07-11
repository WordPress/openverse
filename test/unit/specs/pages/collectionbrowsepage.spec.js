import ClientCollectionBrowsePage from '@/pages/client/CollectionBrowsePage';
import ServerCollectionBrowsePage from '@/pages/server/CollectionBrowsePage';
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
    const wrapper = render(ClientCollectionBrowsePage);
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined();
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined();
  });

  it('should dispatch FETCH_COLLECTION_IMAGES', () => {
    const params = { foo: 'bar' };
    const wrapper = render(ClientCollectionBrowsePage, options);
    wrapper.vm.getImages(params);
    expect(options.mocks.$store.dispatch).toHaveBeenCalledWith('FETCH_COLLECTION_IMAGES', params);
  });

  it('server side page does not render search grid', () => {
    const wrapper = render(ServerCollectionBrowsePage, options);
    expect(wrapper.find({ name: 'search-grid' }).vm).toBeUndefined();
  });
});
