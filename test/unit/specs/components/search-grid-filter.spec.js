import SearchGridFilter from '@/components/SearchGridFilter';
import render from '../../test-utils/render';

describe('SearchGridFilter', () => {
  let options = {};
  let storeMock = null;
  let props = null;
  beforeEach(() => {
    storeMock = {
      state: {
        isFilterApplied: true,
        isFilterVisible: true,
        imageProviders: [
          {
            provider_name: 'FLickr',
            provider_code: 'flickr',
          },
        ],
        query: 'me',
      },
    };

    props = {
      showProvidersFilter: true,
    };

    options = {
      propsData: props,
      mocks: {
        $store: storeMock,
      },
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.find({ name: 'search-grid-filter' }).element).toBeDefined();
  });

  it('should show search filters when isFilterVisible is true', () => {
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.find('.search-filters').classes()).toContain('search-filters__visible');
  });

  it('should not show search filters when isFilterVisible is false', () => {
    storeMock.state.isFilterVisible = false;
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.find('.search-filters').classes()).not.toContain('search-filters__visible');
  });

  it('display providers filter', () => {
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.find('.search-filters_providers').element).toBeDefined();
  });

  it('should not display providers filter when props is set to false', () => {
    props.showProvidersFilter = false;
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.find('.search-filters_providers').element).not.toBeDefined();
  });

  it('emits a search event when a filter is clicked', () => {
    props.showProvidersFilter = false;
    const wrapper = render(SearchGridFilter, options);
    const checkbox = wrapper.find('#creator-chk');
    checkbox.trigger('click');
    expect(wrapper.emitted().onSearchFilterChanged).toBeTruthy();
  });
});
