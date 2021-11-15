import Vuex from 'vuex'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import PhotoTags from '~/components/PhotoTags'
import { UPDATE_QUERY } from '~/constants/action-types'

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

  it('dispatches an action when a tag is clicked', () => {
    const dispatchMock = jest.fn()
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const storeMock = new Vuex.Store({
      modules: {
        search: { namespaced: true, actions: { [UPDATE_QUERY]: dispatchMock } },
      },
    })
    const opts = {
      localVue,
      propsData: {
        ...props,
      },
      store: storeMock,
    }
    const wrapper = render(PhotoTags, opts)
    wrapper.find('.tag').trigger('click')
    const tagName = wrapper.find('.tag').text()
    const dispatchArgs = dispatchMock.mock.calls[0][1]
    expect(dispatchArgs).toEqual({ q: tagName })
  })
})
