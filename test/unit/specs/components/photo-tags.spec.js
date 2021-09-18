import PhotoTags from '~/components/PhotoTags'
import { SET_QUERY } from '~/constants/mutation-types'
import render from '../../test-utils/render'

describe('PhotoTags', () => {
  let options = null
  let props = null

  beforeEach(() => {
    props = {
      tags: [
        {
          accuracy: 1,
          name: 'foo',
          provider: 'clarifai',
        },
        {
          accuracy: 1,
          name: 'bar',
          provider: 'foo',
        },
      ],
    }

    options = {
      propsData: props,
    }
  })

  it('should render correct contents when tags array is not empty', () => {
    const wrapper = render(PhotoTags, options)
    expect(wrapper.find('.photo_tags').element).toBeDefined()
    expect(wrapper.findAll('.tag').length).toBe(2)
  })

  it('should render nothing when tags array is empty', () => {
    options.propsData.tags = []
    const wrapper = render(PhotoTags, options)
    expect(wrapper.find('.photo_tags').element).toBeUndefined()
  })

  it('commits a mutation when a tag is clicked', () => {
    const storeMock = {
      commit: jest.fn(),
    }
    const opts = {
      propsData: {
        ...props,
      },
      mocks: {
        $store: storeMock,
      },
    }
    const wrapper = render(PhotoTags, opts)
    wrapper.find('.tag').trigger('click')
    const tagName = wrapper.find('.tag').text()
    expect(storeMock.commit).toHaveBeenCalledWith(SET_QUERY, {
      query: { q: tagName },
    })
  })
})
