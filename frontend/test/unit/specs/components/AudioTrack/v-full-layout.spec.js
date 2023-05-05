import { fireEvent, render, screen } from "@testing-library/vue"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { useAnalytics } from "~/composables/use-analytics"
import { AUDIO } from "~/constants/media"

import VFullLayout from "~/components/VAudioTrack/layouts/VFullLayout.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(() => ({
    sendCustomEvent: jest.fn(),
  })),
}))

describe("VFullLayout", () => {
  it("should render the weblink button with the foreign landing url", () => {
    const audio = getAudioObj()

    render(VFullLayout, {
      propsData: {
        audio,
        size: "s",
        status: "playing",
        currentTime: 1,
      },
    })

    const downloadButton = screen.getByText("audio-details.weblink")
    expect(downloadButton).toHaveAttribute("href", audio.foreign_landing_url)
  })

  it("should send GET_MEDIA analytics event on button click", async () => {
    const sendCustomEventMock = jest.fn()
    useAnalytics.mockImplementation(() => ({
      sendCustomEvent: sendCustomEventMock,
    }))
    const audio = getAudioObj()

    render(VFullLayout, {
      propsData: {
        audio,
        size: "s",
        status: "playing",
        currentTime: 1,
      },
    })

    const downloadButton = screen.getByText("audio-details.weblink")
    await fireEvent.click(downloadButton)

    expect(sendCustomEventMock).toHaveBeenCalledWith("GET_MEDIA", {
      id: audio.id,
      mediaType: AUDIO,
      provider: audio.provider,
    })
  })
})
