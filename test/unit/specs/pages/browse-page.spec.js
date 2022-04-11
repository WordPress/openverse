import { render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import { ref } from '@nuxtjs/composition-api'
import { createPinia, PiniaVuePlugin } from 'pinia'

import SearchIndex from '~/pages/search.vue'
import { IMAGE } from '~/constants/media'

import { useSearchStore } from '~/stores/search'

describe('SearchIndex', () => {
  let options
  let localVue
  let pinia
  let searchStore

  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(PiniaVuePlugin)
    pinia = createPinia()
    searchStore = useSearchStore(pinia)
    searchStore.setSearchTerm('cat')
    searchStore.setSearchType(IMAGE)
    options = {
      localVue,
      pinia,
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
