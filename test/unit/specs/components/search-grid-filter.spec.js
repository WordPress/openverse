import SearchGridFilter from '~/components/Filters/SearchGridFilter'
import render from '../../test-utils/render'

describe('SearchGridFilter', () => {
  let options = {}
  let storeMock = null
  let dispatchMock = null
  let commitMock = null
  let props = null
  beforeEach(() => {
    dispatchMock = jest.fn()
    commitMock = jest.fn()
    storeMock = {
      dispatch: dispatchMock,
      commit: commitMock,
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
          mature: false,
        },
        query: 'me',
      },
    }

    props = {
      showProvidersFilter: true,
      provider: undefined,
    }

    options = {
      propsData: props,
      mocks: {
        $store: storeMock,
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(SearchGridFilter, options)
    expect(wrapper.find({ name: 'search-grid-filter' }).element).toBeDefined()
  })

  it('should show search filters when isFilterVisible is true', () => {
    const wrapper = render(SearchGridFilter, options)
    expect(wrapper.find('.search-filters').classes()).toContain(
      'search-filters__visible'
    )
  })

  it('should not show search filters when isFilterVisible is false', () => {
    storeMock.state.isFilterVisible = false
    const wrapper = render(SearchGridFilter, options)
    expect(wrapper.find('.search-filters').classes()).not.toContain(
      'search-filters__visible'
    )
  })

  it('should not display providers filter when props is set to false', () => {
    props.showProvidersFilter = false
    const wrapper = render(SearchGridFilter, options)
    expect(wrapper.find('.search-filters_providers').element).not.toBeDefined()
  })

  it('toggles filter', () => {
    const wrapper = render(SearchGridFilter, options)
    wrapper.vm.onUpdateFilter({ code: 'foo', filterType: 'bar' })
    expect(dispatchMock).toHaveBeenCalledWith('TOGGLE_FILTER', {
      code: 'foo',
      filterType: 'bar',
      provider: props.provider,
    })
  })

  it('toggles filter of search by creator', () => {
    const wrapper = render(SearchGridFilter, options)
    wrapper.vm.onUpdateSearchByCreator()
    expect(dispatchMock).toHaveBeenCalledWith('TOGGLE_FILTER', {
      filterType: 'searchBy',
      provider: props.provider,
    })
  })

  it('clears filters', () => {
    const wrapper = render(SearchGridFilter, options)
    wrapper.vm.onClearFilters()
    expect(commitMock).toHaveBeenCalledWith('CLEAR_FILTERS', {
      provider: props.provider,
    })
  })

  it('toggles search visibility', () => {
    const wrapper = render(SearchGridFilter, options)
    wrapper.vm.onToggleSearchGridFilter()
    expect(commitMock).toHaveBeenCalledWith('SET_FILTER_IS_VISIBLE', {
      isFilterVisible: !storeMock.state.isFilterVisible,
    })
  })
})
