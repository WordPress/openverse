import { vi } from "vitest"
import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useSearchStore } from "~/stores/search"

import { useAnalytics } from "~/composables/use-analytics"
import { ALL_MEDIA } from "~/constants/media"

import VSearchGridFilter from "~/components/VFilters/VSearchGridFilter.vue"

vi.mock("~/composables/use-analytics")
describe("VSearchGridFilter", () => {
  let options = {}
  let searchStore
  let configureStoreCb
  const routerMock = { push: vi.fn() }
  const routeMock = { path: vi.fn() }
  const sendCustomEventMock = vi.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))

  beforeEach(() => {
    sendCustomEventMock.mockClear()

    options = {
      mocks: {
        $route: routeMock,
        $router: routerMock,
      },
    }
    configureStoreCb = (localVue, options) => {
      searchStore = useSearchStore(options.pinia)
    }
  })

  it("toggles filter", async () => {
    await render(VSearchGridFilter, options)
    const checked = screen.queryAllByRole("checkbox", { checked: true })
    expect(checked.length).toBe(0)
    await fireEvent.click(
      screen.queryByRole("checkbox", { name: /use commercially/i })
    )
    // `getBy` serves as expect because it throws an error if no element is found
    screen.getByRole("checkbox", { checked: true, name: /use commercially/i })
  })

  it("sends APPLY_FILTER event when filter is toggled", async () => {
    configureStoreCb = (localVue, options) => {
      searchStore = useSearchStore(options.pinia)
      searchStore.setSearchTerm("cat")
    }
    await render(VSearchGridFilter, options, configureStoreCb)

    await fireEvent.click(
      screen.queryByRole("checkbox", { name: /use commercially/i })
    )
    expect(sendCustomEventMock).toHaveBeenCalledWith("APPLY_FILTER", {
      category: "licenseTypes",
      key: "commercial",
      checked: true,
      query: "cat",
      searchType: ALL_MEDIA,
    })
  })

  it("clears filters", async () => {
    configureStoreCb = (localVue, options) => {
      searchStore = useSearchStore(options.pinia)
      searchStore.toggleFilter({ filterType: "licenses", code: "by" })
    }
    await render(VSearchGridFilter, options, configureStoreCb)
    // if no checked checkboxes were found, this would raise an error
    screen.getByRole("checkbox", { checked: true })

    await fireEvent.click(screen.getByText("Clear filters"))
    const checkedFilters = screen.queryAllByRole("checkbox", { checked: true })
    const uncheckedFilters = screen.queryAllByRole("checkbox", {
      checked: false,
    })

    expect(checkedFilters.length).toBe(0)
    // Filters are reset with the initial `filterData` for ALL_MEDIA
    expect(uncheckedFilters.length).toBe(10)
  })
})
