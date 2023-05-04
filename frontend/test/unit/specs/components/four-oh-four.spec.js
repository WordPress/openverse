import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VFourOhFour from "~/components/VFourOhFour.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))
describe("VFourOhFour", () => {
  let options
  const sendCustomEventMock = jest.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))
  const query = "cat"
  beforeEach(() => {
    options = {
      mocks: { $router: { push: jest.fn() } },
    }
  })

  it("should send SUBMIT_SEARCH analytics event when search submitted", async () => {
    render(VFourOhFour, options)

    const input = screen.getByRole("searchbox")
    await fireEvent.update(input, query)
    await fireEvent.submit(input)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query,
      searchType: "all",
    })
  })
})
