import SearchGrid from '~/components/SearchGridManualLoad'
import render from '../../test-utils/render'
import { SET_MEDIA } from '~/constants/mutation-types'
import filterStore from '~/store/filter'
import searchStore from '~/store/search'

import Vuex from 'vuex'
import { IMAGE } from '~/constants/media'
describe('SearchGrid', () => {
  let options = {}
  let commitMock = null
  let storeMock
  let searchStoreMock

  beforeEach(() => {
    commitMock = jest.fn()
    searchStoreMock = {
      state: {
        images: [{ id: 'foo', title: 'image1.jpg' }],
        imagesCount: 1,
        imagePage: 1,
        isFetching: {
          images: false,
        },
        isFetchingError: {
          images: false,
        },
        pageCount: {
          images: 2,
        },
        searchType: IMAGE,
      },
      getters: searchStore.getters,
      actions: searchStore.actions,
      mutations: {
        ...searchStore.mutations,
        [SET_MEDIA]: commitMock,
      },
    }
    storeMock = new Vuex.Store({
      modules: {
        filter: {
          namespaced: true,
          ...filterStore,
        },
        search: {
          namespaced: true,
          ...searchStoreMock,
        },
      },
    })
    options = {
      store: storeMock,
      stubs: {
        SaferBrowsing: true,
        LoadingIcon: true,
        MetaSearchForm: true,
        SearchGridCell: true,
        SearchRating: true,
      },
      propsData: {
        includeAnalytics: true,
      },
      mocks: {
        $store: storeMock,
        store: storeMock,
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.find('section').element).toBeDefined()
    expect(wrapper.find('.load-more').element).toBeDefined()
  })

  it("doesn't render load more button if not loading images", () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.find('.load-more').element).toBeDefined()
  })

  it("doesn't render load more button if is loading images", () => {
    options.mocks.$store.state.search.isFetching.images = true
    const wrapper = render(SearchGrid, options)
    expect(wrapper.find('.load-more').vm).not.toBeDefined()
  })

  it('shows loading icon if is loading images', () => {
    options.mocks.$store.state.search.isFetching.images = true

    const wrapper = render(SearchGrid, options)
    expect(wrapper.findComponent({ name: 'LoadingIcon' })).toBeDefined()
  })

  it("doesn't render load more button if not loading images", async () => {
    const wrapper = render(SearchGrid, options)
    const button = wrapper.find('.button')
    await button.trigger('click')

    expect(wrapper.emitted('onLoadMoreImages')[0]).toEqual([
      {
        page: 2,
        shouldPersistMedia: true,
        ...options.propsData.query,
      },
    ])
  })
  // TODO: SearchGrid should be replaced with ImageGrid, and tested with testing library
  // it('sets image to empty array on search changed', () => {
  //   const wrapper = render(SearchGrid, options)
  //   wrapper.vm.searchChanged()
  //
  //   expect(commitMock).toHaveBeenLastCalledWith(`${SEARCH}/${SET_MEDIA}`, {
  //     media: [],
  //     page: 1,
  //   })
  // })
})
