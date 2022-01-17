import SearchIndex from '~/pages/search.vue'
import { render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import { ref } from '@nuxtjs/composition-api'

describe('SearchIndex', () => {
  let options
  let localVue
  let storeMock
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    storeMock = new Vuex.Store({
      modules: {
        search: {
          namespaced: true,
          state: {
            query: { q: 'foo', mediaType: 'image' },
            searchType: 'image',
          },
          getters: {
            isAnyFilterApplied: () => false,
            appliedFilterTags: () => [],
          },
        },
        media: {
          namespaced: true,
          getters: {
            fetchState: () => ({ isFetching: false }),
            results: () => ({ count: 0 }),
          },
        },
      },
    })
    options = {
      localVue,
      store: storeMock,
      mocks: {
        $router: { path: { name: 'search-image' } },
        $route: { path: '/search/image' },
      },
      stubs: { NuxtChild: true, VSearchGrid: true },
    }
  })

  it('hides the scroll button when injected value is false', () => {
    options.provide = { showScrollButton: ref(false) }

    render(SearchIndex, options)

    expect(screen.queryByLabelText(/scroll/i)).not.toBeVisible()
  })

  it('shows the scroll button when injected value is false', () => {
    options.provide = { showScrollButton: ref(true) }

    render(SearchIndex, options)

    expect(screen.queryByLabelText(/scroll/i)).toBeVisible()
  })
})
