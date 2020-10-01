import SearchGrid from '~/components/SearchGridManualLoad'
import render from '../../test-utils/render'
describe('SearchGrid', () => {
  let options = {}
  let commitMock = null

  beforeEach(() => {
    commitMock = jest.fn()
    options = {
      propsData: {
        query: { q: 'foo' },
        includeAnalytics: true,
        isFetchingImages: false,
      },
      mocks: {
        $store: {
          state: {
            imagesCount: 100,
            imagePage: 1,
          },
          commit: commitMock,
        },
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.findComponent('section').element).toBeDefined()
    expect(wrapper.findComponent('.load-more').element).toBeDefined()
  })

  it('doesnt render load more button if not loading images', () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.findComponent('.load-more').element).toBeDefined()
  })

  it('doesnt render load more button if is loading images', () => {
    options.propsData.isFetchingImages = true
    const wrapper = render(SearchGrid, options)
    expect(wrapper.findComponent('.load-more').vm).not.toBeDefined()
  })

  it('shows loading icon if is loading images', () => {
    options.propsData.isFetchingImages = true
    const wrapper = render(SearchGrid, options)
    expect(wrapper.findComponent({ name: 'LoadingIcon' }).vm).toBeDefined()
  })

  it('doesnt render load more button if not loading images', () => {
    const wrapper = render(SearchGrid, options)
    const button = wrapper.findComponent('.button')
    button.trigger('click')

    expect(wrapper.emitted('onLoadMoreImages')[0]).toEqual([
      {
        page: 2,
        shouldPersistImages: true,
        ...options.propsData.query,
      },
    ])
  })

  it('sets image to empty array on search changed', () => {
    const wrapper = render(SearchGrid, options)
    wrapper.vm.searchChanged()

    expect(commitMock).toHaveBeenCalledWith('SET_IMAGES', {
      images: [],
      page: 1,
    })
  })
})
