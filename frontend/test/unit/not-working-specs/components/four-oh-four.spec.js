import { fireEvent, screen } from "@testing-library/vue"

import { vi } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import VFourOhFour from "~/components/VFourOhFour.vue"

const sendCustomEventMock = vi.fn()

vi.mock("~/composables/use-analytics", () => ({
  useAnalytics: () => ({
    sendCustomEvent: sendCustomEventMock,
  }),
}))

describe("VFourOhFour", () => {
  let options
  const query = "cat"

  it("should send SUBMIT_SEARCH analytics event when search submitted", async () => {
    await render(VFourOhFour, options)

    const input = screen.getByRole("searchbox")
    await fireEvent.update(input, query)
    await fireEvent.submit(input)

    expect(sendCustomEventMock()).toHaveBeenCalledWith("SUBMIT_SEARCH", {
      query,
      searchType: "all",
    })
  })
})
