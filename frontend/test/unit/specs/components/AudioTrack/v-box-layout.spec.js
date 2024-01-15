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
    options = { props }
  })

  it("renders audio title, license and category in v-box-layout", async () => {
    props.audio.category = "music"
    await render(VBoxLayout, options)
    const title = screen.getByText(props.audio.title)
    expect(title).toBeVisible()
    const license = screen.getByLabelText(
      "Attribution-NonCommercial-Share-Alike"
    )
    expect(license).toBeInTheDocument() // Not visible unless hovered
    const category = screen.getByText("Music")
    expect(category).toBeVisible()
  })

  it("should not render category string if category is null", async () => {
    props.audio.category = null
    await render(VBoxLayout, options)
    const categoryLabel = screen.queryByText("Music")
    expect(categoryLabel).toBeNull()
  })
})
