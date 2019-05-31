import CollectionsPage from '@/pages/CollectionsPage';
import render from '../../test-utils/render';

describe('CollectionsPage', () => {
  const options = {
    mocks: {
      $store: {
        state: {
          imageProviders: [
            { provider_name: 'met' },
            { provider_name: 'flickr' },
          ],
        },
        dispatch: jest.fn(),
      },
    },
  };
  it('should render correct contents', () => {
    const wrapper = render(CollectionsPage, options);
    expect(wrapper.findAll({ name: 'collection-item' }).length).toBe(2);
  });

  it('should get museum providers', () => {
    const wrapper = render(CollectionsPage, options);
    const museumProviders = wrapper.vm.museumProviders;
    expect(museumProviders[0].provider_name).toBe('met');
  });

  it('should get museum providers', () => {
    const wrapper = render(CollectionsPage, options);
    const museumProviders = wrapper.vm.otherProviders;
    expect(museumProviders[0].provider_name).toBe('flickr');
  });

  it('should get all providers', () => {
    const wrapper = render(CollectionsPage, options);
    const museumProviders = wrapper.vm.providers;
    expect(museumProviders).toHaveLength(2);
  });
});
