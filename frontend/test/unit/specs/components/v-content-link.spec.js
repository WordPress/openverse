import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VContentLink from "~/components/VContentLink/VContentLink.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

describe("VContentLink", () => {
  let options = {}

  beforeEach(() => {
    options = {
      props: { mediaType: "image", resultsCount: 123, to: "/images" },
    }
  })

  it("is enabled when there are results", () => {
    render(VContentLink, options)
    const btn = screen.getByRole("link")

    expect(btn).toHaveAttribute("href")
    expect(btn).not.toHaveAttribute("aria-disabled")
  })

  it("sends CHANGE_CONTENT_TYPE event when clicked", async () => {
    const sendCustomEventMock = jest.fn()

    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    render(VContentLink, options)
    const btn = screen.getByRole("link")

    await fireEvent.click(btn)
    expect(sendCustomEventMock).toHaveBeenCalledWith("CHANGE_CONTENT_TYPE", {
      component: "VContentLink",
      next: "image",
      previous: "all",
    })
  })
})
