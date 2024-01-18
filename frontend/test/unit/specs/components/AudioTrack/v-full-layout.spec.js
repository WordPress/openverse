import { getAudioObj } from "~~/test/unit/fixtures/audio"
import { render } from "~~/test/unit/test-utils/render"

import VFullLayout from "~/components/VAudioTrack/layouts/VFullLayout.vue"

describe("VFullLayout", () => {
  it("should render the weblink button with the foreign landing url", async () => {
    const audio = getAudioObj()

    const { getByText } = await render(VFullLayout, {
      props: {
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
