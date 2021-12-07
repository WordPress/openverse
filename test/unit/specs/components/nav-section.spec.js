import Vuex from 'vuex'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import NavSection from '~/components/NavSection'
import { UPDATE_QUERY } from '~/constants/action-types'
import { IMAGE } from '~/constants/media'

describe('NavSection', () => {
  it('dispatches an action when the form is submitted', async () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const dispatchMock = jest.fn()
    const storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          state: {
            query: { q: 'foo', mediaType: IMAGE },
          },
          actions: {
            [UPDATE_QUERY]: dispatchMock,
          },
        },
      },
    })
    const routerMock = { push: jest.fn() }
    const options = {
      localVue,
      propsData: {
        fixedNav: null,
        showNavSearch: 'true',
      },
      store: storeMock,
      mocks: { $router: routerMock },
      stubs: { NuxtLink: true },
    }

    const wrapper = render(NavSection, options)
    wrapper.find('.search-form').trigger('submit')
    expect(routerMock.push).toHaveBeenCalledWith({
      path: '/search/image',
      query: { q: 'foo' },
    })
    const dispatchArgs = dispatchMock.mock.calls[0][1]
    expect(dispatchArgs).toEqual({ q: 'foo' })
  })
})
