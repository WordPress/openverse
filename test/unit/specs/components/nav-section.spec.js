import Vuex from 'vuex'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import NavSection from '~/components/NavSection'
import { UPDATE_QUERY } from '~/constants/action-types'

describe('NavSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(NavSection, { stubs: { NuxtLink: true } })
    expect(wrapper.find('nav').vm).toBeDefined()
  })

  it('dispatches an action when the form is submitted', async () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const dispatchMock = jest.fn()
    const storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
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
    await wrapper.setData({ form: { searchTerm: 'foo' } })
    wrapper.find('.hero_search-form').trigger('submit')
    expect(routerMock.push).toHaveBeenCalledWith({
      path: '/search',
      query: { q: 'foo' },
    })
    const dispatchArgs = dispatchMock.mock.calls[0][1]
    expect(dispatchArgs).toEqual({ q: 'foo' })
  })
})
