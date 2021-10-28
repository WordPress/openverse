import { render } from '@testing-library/vue'

import FilterDisplay from '~/components/Filters/FilterDisplay'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'

describe('FilterDisplay', () => {
  const localVue = createLocalVue()
  localVue.use(Vuex)
  const storeMock = new Vuex.Store({
    modules: {
      search: {
        namespaced: true,
        state: {
          query: {
            q: 'foo',
          },
        },
      },
      filter: {
        namespaced: true,
        getters: {
          isAnyFilterApplied: () => true,
          appliedFilterTags: () => [
            {
              code: 'cc0',
              filterType: 'license',
              name: 'filters.licenses.cc0',
            },
          ],
        },
      },
    },
  })
  const options = {
    localVue,
    store: storeMock,
  }

  it('should render correct contents', () => {
    const { container } = render(FilterDisplay, options)
    expect(container.firstChild).toMatchSnapshot()
  })
})
