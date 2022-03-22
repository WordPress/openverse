import { render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import { ref } from '@nuxtjs/composition-api'
import { createPinia, PiniaVuePlugin } from 'pinia'

import SearchIndex from '~/pages/search.vue'
import { IMAGE } from '~/constants/media'

import { useSearchStore } from '~/stores/search'

describe('SearchIndex', () => {
  let options
  let localVue
  let storeMock
  let pinia
  let searchStore
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(PiniaVuePlugin)
    pinia = createPinia()
    searchStore = useSearchStore(pinia)
    searchStore.setSearchTerm('cat')
    searchStore.setSearchType(IMAGE)
    storeMock = new Vuex.Store({
      modules: {
        media: {
          namespaced: true,
          getters: {
            fetchState: () => ({ isFetching: false }),
            resultCount: () => 0,
            results: () => ({ count: 0 }),
          },
        },
      },
    })
    options = {
      localVue,
      pinia,
      store: storeMock,
      mocks: {
        $router: { path: { name: 'search-image' } },
        $route: { path: '/search/image' },
      },
      stubs: {
        NuxtChild: true,
        VSearchGrid: true,
        VSkipToContentContainer: true,
      },
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
