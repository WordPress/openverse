import { screen } from "@testing-library/vue"

import { getAudioObj } from "~~/test/unit/fixtures/audio"
import { render } from "~~/test/unit/test-utils/render"

import VBoxLayout from "~/components/VAudioTrack/layouts/VBoxLayout.vue"

describe("VBoxLayout", () => {
  let options = null
  let props = {
    audio: getAudioObj(),
    size: "m",
  }

  beforeEach(() => {
    options = {
      propsData: props,
    }
  })

  it("renders audio title, license and category in v-box-layout", () => {
    props.audio.category = "music"
    render(VBoxLayout, options)
    expect(() => {
      screen.getByText(props.audio.title)
      screen.getByLabelText("Attribution-NonCommercial-Share-Alike")
      screen.getByText("Music")
    }).not.toThrow()
  })

  it("should not render category string if category is null", () => {
    props.audio.category = null
    render(VBoxLayout, options)
    const categoryLabel = screen.queryByText("Music")
    expect(categoryLabel).toBeNull()
  })
})
