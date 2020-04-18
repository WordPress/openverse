
import SearchGridFilter from '@/components/SearchGridFilter';
import { filterData } from '@/store/filter-store';
import render from '../../test-utils/render';

describe('SearchGridFilter', () => {
  let options = {};
  let storeMock = null;
  let dispatchMock = null;
  let props = null;
  beforeEach(() => {
    dispatchMock = jest.fn();
    storeMock = {
      dispatch: dispatchMock,
      state: {
        isFilterApplied: true,
        isFilterVisible: true,
        filters: {
          licenseTypes: [{ code: 'commercial', name: 'Commercial usage' }],
          licenses: [{ code: 'by', name: 'CC-BY' }],
          categories: [{ code: 'photo', name: 'Photographs' }],
          extensions: [{ code: 'jpg', name: 'JPG' }],
          searchBy: {
            creator: false,
          },
        },
        query: 'me',
      },
    };

    props = {
      showProvidersFilter: true,
      isCollectionsPage: false,
      provider: undefined,
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

  it('display filters', () => {
    const wrapper = render(SearchGridFilter, options);
    expect(wrapper.findAll({ name: 'filter-check-list' }).length).toBe(Object.keys(filterData).length - 1);
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
    expect(dispatchMock).toHaveBeenCalledWith('TOGGLE_FILTER', {
      filterType: 'searchBy',
      isCollectionsPage: props.isCollectionsPage,
      provider: props.provider,
      shouldNavigate: true,
    });
  });
});
