import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VHeaderInternal from "~/components/VHeader/VHeaderInternal.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))

jest.mock("@nuxtjs/composition-api", () => {
  const { ref } = require("vue")
  return {
    useRoute: jest.fn().mockReturnValue(
      ref({
        name: "route_name__extra",
      })
    ),
  }
})

describe("VHeaderInternal", () => {
  let options = null
  const sendCustomEventMock = jest.fn()

  beforeEach(() => {
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    options = {
      stubs: ["ClientOnly"],
    }
  })

  it("sends OPEN_PAGES_MENU analytics event when pages menu triggered", async () => {
    const screen = render(VHeaderInternal, options)
    const pagesMenuTrigger = screen.getByLabelText("menu")

    await fireEvent.click(pagesMenuTrigger)

    expect(sendCustomEventMock).toHaveBeenCalledWith("OPEN_PAGES_MENU", {})

    await fireEvent.click(pagesMenuTrigger)
  })
})
