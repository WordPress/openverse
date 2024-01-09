import { render } from "@testing-library/vue"

import { getAudioObj } from "~~/test/unit/fixtures/audio"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VFullLayout from "~/components/VAudioTrack/layouts/VFullLayout.vue"

describe("VFullLayout", () => {
  it("should render the weblink button with the foreign landing url", () => {
    const audio = getAudioObj()

    const { getByText } = render(VFullLayout, {
      global: { plugins: [i18n] },
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
