import PhotoDetailPage from '~/pages/photos/_id'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'

describe('PhotoDetailPage', () => {
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
          image: {
            id: 1,
            tags: ['one', 'two', 'three'],
          },
        },
        dispatch: jest.fn(),
      },
      $t,
    },
  }
  it('should render correct contents', () => {
    const wrapper = render(PhotoDetailPage, options)

    expect(wrapper.find({ name: 'PhotoDetails' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'PhotoTags' }).vm).toBeDefined()
  })
})
