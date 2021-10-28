import NavSection from '~/components/NavSection'
import { SET_Q } from '~/constants/mutation-types'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

describe('NavSection', () => {
  it('should render correct contents', () => {
    const wrapper = render(NavSection, { stubs: { NuxtLink: true } })
    expect(wrapper.find('nav').vm).toBeDefined()
  })

  it('commits a mutation when the form is submitted', async () => {
    const localVue = createLocalVue()
    localVue.use(Vuex)
    const commitMock = jest.fn()
    const storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          mutations: {
            [SET_Q]: commitMock,
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
    // The first parameter should be the commit type, but because of the way it's mocked, it's {}
    expect(commitMock).toHaveBeenLastCalledWith({}, { q: 'foo' })
  })
})
