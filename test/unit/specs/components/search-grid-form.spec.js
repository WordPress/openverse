import SearchGridForm from '~/components/SearchGridForm'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

const localVue = createLocalVue()
localVue.use(Vuex)
const storeMock = new Vuex.Store({
  modules: {
    search: {
      namespaced: true,
      state: { query: { q: 'foo' }, isFilterVisible: true },
    },
  },
})

describe('SearchGridForm', () => {
  it('should render correct contents', () => {
    const wrapper = render(SearchGridForm, {
      localVue,
      mocks: {
        $route: {
          path: '/search',
        },
      },
      store: storeMock,
    })

    expect(wrapper.find('form').vm).toBeDefined()
  })
})
