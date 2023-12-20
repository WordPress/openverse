import { fireEvent } from "@testing-library/vue"

import { ref } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VHeaderDesktop from "~/components/VHeader/VHeaderDesktop.vue"

vi.mock("~/composables/use-analytics", () => ({
  useAnalytics: vi.fn(),
}))
vi.mock("~/composables/use-match-routes", () => ({
  // mocking `Ref<boolean>` as `{ value: boolean }`
  useMatchSearchRoutes: vi.fn(() => ({ matches: { value: true } })),
}))

describe("VHeaderDesktop", () => {
  const sendCustomEventMock = vi.fn()
  window.scrollTo = vi.fn()

  let options = null

  beforeEach(() => {
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    options = {
      provide: {
        [IsHeaderScrolledKey]: ref(false),
        [IsSidebarVisibleKey]: ref(false),
      },
    }
  })
  it("sends SUBMIT_SEARCH analytics event when submitted", async () => {
    const screen = await render(VHeaderDesktop, options)
    const input = screen.getByRole("combobox")

    await fireEvent.update(input, "cat")
    await fireEvent.submit(input)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query: "cat",
      searchType: "all",
    })
  })

  it("sends TOGGLE_FILTER_SIDEBAR analytics event when the filter sidebar is opened", async () => {
    const screen = await render(VHeaderDesktop, options)
    const filterSidebarTrigger = screen.getByText("Filters")

    await fireEvent.click(filterSidebarTrigger)

    expect(sendCustomEventMock).toHaveBeenCalledWith("TOGGLE_FILTER_SIDEBAR", {
      searchType: "all",
      toState: "opened",
    })
  })

  describe("when the filter sidebar is visible", () => {
    beforeEach(() => {
      options.provide[IsSidebarVisibleKey] = ref(true)
    })

    it("sends TOGGLE_FILTER_SIDEBAR analytics event when the filter sidebar is closed", async () => {
      const screen = await render(VHeaderDesktop, options)
      const filterSidebarTrigger = screen.getByText("Filters")

      await fireEvent.click(filterSidebarTrigger)

      expect(sendCustomEventMock).toHaveBeenCalledWith(
        "TOGGLE_FILTER_SIDEBAR",
        {
          searchType: "all",
          toState: "closed",
        }
      )
    })
  })
})
