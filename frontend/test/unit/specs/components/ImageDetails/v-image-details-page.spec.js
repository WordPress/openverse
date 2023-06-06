import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"
import { IMAGE } from "~/constants/media"

import VImageDetailsPage from "~/pages/image/_id/index.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(() => ({
    sendCustomEvent: jest.fn(),
  })),
}))

jest.mock("~/stores/media/single-result", () => ({
  useSingleResultStore: jest.fn(() => ({
    mediaType: "image",
    mediaItem: imageObject,
  })),
}))

const imageObject = {
  id: "123",
  provider: "test-provider",
  foreign_landing_url: "https://test.com",
  frontendMediaType: "image",
}

describe("VImageDetailsPage", () => {
  it("should send GET_MEDIA analytics event on CTA button click", async () => {
    const sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))

    render(VImageDetailsPage, {
      mocks: {
        $route: {
          params: {
            meta: "url",
          },
        },
      },
    })

    const downloadButton = screen.getByText(/get this image/i)
    await fireEvent.click(downloadButton)

    expect(sendCustomEventMock).toHaveBeenCalledWith("GET_MEDIA", {
      id: imageObject.id,
      mediaType: IMAGE,
      provider: imageObject.provider,
    })
  })
})
