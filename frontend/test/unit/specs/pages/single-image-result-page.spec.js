import { fireEvent } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { IMAGE } from "~/constants/media"
import { useSingleResultStore } from "~/stores/media/single-result"
import { useAnalytics } from "~/composables/use-analytics"

import SingleImageResultPage from "~/pages/image/_id/index.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(),
}))
describe("SingleImageResultPage", () => {
  let options
  let singleImageStore
  const id = "123"
  const sendCustomEventMock = jest.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))

  it("should send RIGHT_CLICK_IMAGE analytics event", async () => {
    const screen = render(
      SingleImageResultPage,
      options,
      (localVue, options) => {
        singleImageStore = useSingleResultStore(options.pinia)
        singleImageStore.mediaType = IMAGE
        singleImageStore.mediaItem = {
          frontendMediaType: IMAGE,
          id,
          url: "http://example.com/image.jpg",
          width: 100,
          height: 100,
          providerName: "provider",
        }
      }
    )
    const image = await screen.findByRole("img")
    await fireEvent.contextMenu(image)
    expect(sendCustomEventMock).toHaveBeenCalledWith("RIGHT_CLICK_IMAGE", {
      id,
    })
  })
})
