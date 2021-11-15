import SearchGrid from '~/components/SearchGrid'
import render from '../../test-utils/render'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

const localVue = createLocalVue()
localVue.use(Vuex)
const storeMock = new Vuex.Store({
  modules: {
    search: {
      namespaced: true,
      state: {
        query: { q: 'foo' },
        filters: {
          licenseTypes: [
            { code: 'commercial', name: 'Commercial usage' },
            { code: 'modification', name: 'Allows modification' },
          ],
        },
      },
    },
  },
})

const options = {
  stubs: {
    ScrollButton: true,
    SearchGridManualLoad: true,
  },
  localVue,
  store: storeMock,
}

describe('Search Grid Wrapper', () => {
  it('renders correct content', () => {
    const wrapper = render(SearchGrid, options)
    expect(wrapper.find('[data-testid="search-grid"]').element).toBeDefined()
  })
})
