import CollectionBrowsePage from '@/pages/CollectionBrowsePage'
import render from '../../test-utils/render';
import i18n from '../../test-utils/i18n';

describe('CollectionBrowsePage', () => {
  const $t = (key) => i18n.messages[key]
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
      $t,
    },
  }

  it('should render correct contents', () => {
    const wrapper = render(CollectionBrowsePage)
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined()
  })

  it('should dispatch FETCH_COLLECTION_IMAGES', () => {
    const params = { foo: 'bar' }
    const wrapper = render(CollectionBrowsePage, options)
    wrapper.vm.getImages(params)
    expect(options.mocks.$store.dispatch).toHaveBeenCalledWith(
      'FETCH_COLLECTION_IMAGES',
      params
    )
  })
})
