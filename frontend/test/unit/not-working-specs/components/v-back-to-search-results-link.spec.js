import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"

vi.mock("~/composables/use-analytics", () => ({
  useAnalytics: vi.fn(),
}))

describe("VBackToSearchResultsLink", () => {
  it("should send analytics event when clicked", async () => {
    const sendCustomEventMock = vi.fn()

    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))

    const props = {
      id: "123",
      href: "/search",
    }

    const screen = await render(VBackToSearchResultsLink, {
      props,
    })
    const link = screen.getByText(/back to results/i)

    await fireEvent.click(link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("BACK_TO_SEARCH", {
      id: props.id,
      searchType: "all",
    })
  })
})
