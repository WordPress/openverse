import { createLocalVue } from "@vue/test-utils"
import { fireEvent, render } from "@testing-library/vue"

import { PiniaVuePlugin, createPinia } from "~~/test/unit/test-utils/pinia"

import { useAnalytics } from "~/composables/use-analytics"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(() => ({
    sendCustomEvent: jest.fn(),
  })),
}))

const localVue = createLocalVue()
localVue.use(PiniaVuePlugin)
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
      localVue,
      pinia: createPinia(),
      propsData,
    })
    const link = screen.getByText("single-result.back")

    await fireEvent.click(link)

    expect(sendCustomEventMock).toHaveBeenCalledWith("BACK_TO_SEARCH", {
      id: propsData.id,
      searchType: "all",
    })
  })
})
