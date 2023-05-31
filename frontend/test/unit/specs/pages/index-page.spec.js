import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import IndexPage from "~/pages/index.vue"

import { useAnalytics } from "~/composables/use-analytics"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))
describe("IndexPage", () => {
  let options
  const sendCustomEventMock = jest.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))
  const query = "cat"
  beforeEach(() => {
    options = {
      mocks: { $router: { push: jest.fn() } },
      stubs: ["VHomeGallery"],
    }
  })

  it("should send SUBMIT_SEARCH analytics event when search submitted", async () => {
    render(IndexPage, options)

    const input = screen.getByRole("searchbox")
    await fireEvent.update(input, query)
    await fireEvent.submit(input)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query,
      searchType: "all",
    })
  })

  it("should send SUBMIT_SEARCH analytics event with correct mediaType when search submitted", async () => {
    render(IndexPage, options)

    const button = screen.getByRole("button", {
      name: "Select a content type: All content",
    })
    await fireEvent.click(button)

    const audio = screen.getByRole("radio", { name: "Audio" })
    await fireEvent.click(audio)

    const input = screen.getByRole("searchbox")
    await fireEvent.update(input, query)
    await fireEvent.submit(input)

    expect(sendCustomEventMock).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query,
      searchType: "audio",
    })
  })
})
