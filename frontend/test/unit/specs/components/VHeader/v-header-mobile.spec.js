import { fireEvent } from "@testing-library/vue"
import { ref } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import VHeaderMobile from "~/components/VHeader/VHeaderMobile/VHeaderMobile.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))
jest.mock("~/composables/use-match-routes", () => ({
  // mocking `Ref<boolean>` as `{ value: boolean }`
  useMatchSearchRoutes: jest.fn(() => ({ matches: { value: true } })),
}))

describe("VHeaderMobile", () => {
  const routerMock = { push: jest.fn() }
  const sendCustomEventMock = jest.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))
  window.scrollTo = jest.fn()

  let options = null

  beforeEach(() => {
    options = {
      mocks: { $router: routerMock },
      stubs: ["ClientOnly"],
      provide: {
        [IsHeaderScrolledKey]: ref(false),
        [IsSidebarVisibleKey]: ref(false),
      },
    }
  })
  it("sends SUBMIT_SEARCH analytics event when submitted", async () => {
    const screen = render(VHeaderMobile, options)
    const input = screen.getByRole("combobox")

    await fireEvent.update(input, "cat")
    await fireEvent.submit(input)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query: "cat",
      searchType: "all",
    })
  })
})
