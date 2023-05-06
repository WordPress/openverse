import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VBackToSearchResultsLink", () => {
  it("should send analytics event when clicked", async () => {
    const sendCustomEventMock = jest.fn()

    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))

    const propsData = {
      id: "123",
      href: "/search",
    }

    const screen = render(VBackToSearchResultsLink, {
      propsData,
    })
    const link = screen.getByText(/back to results/i)

    await fireEvent.click(link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("BACK_TO_SEARCH", {
      id: propsData.id,
      searchType: "all",
    })
  })
})
