import { getAudioObj } from "~~/test/unit/fixtures/audio"
import { render } from "~~/test/unit/test-utils/render"

import { useAnalytics } from "~/composables/use-analytics"

import VFullLayout from "~/components/VAudioTrack/layouts/VFullLayout.vue"

jest.mock("~/composables/use-analytics")

describe("VFullLayout", () => {
  const sendCustomEventMock = jest.fn()
  useAnalytics.mockImplementation(() => ({
    sendCustomEvent: sendCustomEventMock,
  }))
  beforeEach(() => {
    sendCustomEventMock.mockClear()
  })
  it("should render the weblink button with the foreign landing url", () => {
    const audio = getAudioObj()

    const { getByText } = render(VFullLayout, {
      propsData: {
        audio,
        size: "s",
        status: "playing",
        currentTime: 1,
      },
    })

    const downloadButton = getByText(/Get this audio/i)
    expect(downloadButton).toHaveAttribute("href", audio.foreign_landing_url)
  })
})
