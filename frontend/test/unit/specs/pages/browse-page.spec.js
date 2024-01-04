import { screen } from "@testing-library/vue"
import { ref } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { IMAGE } from "~/constants/media"
import { useSearchStore } from "~/stores/search"

import SearchIndex from "~/pages/search.vue"

import {
  IsHeaderScrolledKey,
  IsSidebarVisibleKey,
  ShowScrollButtonKey,
} from "~/types/provides"

describe("SearchIndex", () => {
  let options
  const defaultProvideOptions = {
    showScrollButton: ref(false),
    [IsHeaderScrolledKey]: ref(false),
    [IsSidebarVisibleKey]: ref(false),
    [ShowScrollButtonKey]: ref(false),
  }
  let searchStore

  beforeEach(() => {
    options = {
      provide: defaultProvideOptions,
      mocks: {
        $router: { path: { name: "search-image" } },
        $route: { path: "/search/image" },
      },
      stubs: {
        NuxtChild: true,
        VSearchGrid: true,
      },
    }
  })

  // TODO: Move these tests to e2e
  // https://github.com/wordpress/openverse/issues/411
  it.skip("hides the scroll button when injected value is false", async () => {
    options.provide.showScrollButton.value = false

    await render(SearchIndex, options, (localVue, options) => {
      searchStore = useSearchStore(options.pinia)
      searchStore.setSearchTerm("cat")
      searchStore.setSearchType(IMAGE)
    })

    expect(screen.queryByLabelText(/scroll/i)).not.toBeVisible()
  })

  // TODO: Move these tests to e2e
  // https://github.com/wordpress/openverse/issues/411
  it.skip("shows the scroll button when injected value is true", async () => {
    options.provide[ShowScrollButtonKey].value = true
    await render(SearchIndex, options, (localVue, options) => {
      searchStore = useSearchStore(options.pinia)
      searchStore.setSearchTerm("cat")
      searchStore.setSearchType(IMAGE)
    })

    expect(screen.queryByLabelText(/scroll/i)).toBeVisible()
  })
})
