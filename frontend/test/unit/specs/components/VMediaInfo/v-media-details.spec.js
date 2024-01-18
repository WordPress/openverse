import { screen } from "@testing-library/vue"

import { getAudioObj } from "~~/test/unit/fixtures/audio"
import { render } from "~~/test/unit/test-utils/render"

import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"

describe("VMediaDetails", () => {
  let options

  const overrides = {
    audio_set: {
      title: "Test Album",
      foreign_landing_url: "https://www.jamendo.com/album/3661/listen",
      creator: "Tryad",
      creator_url: "https://www.jamendo.com/artist/104/tryad",
      url: "https://usercontent.jamendo.com?type=album&id=3661&width=200",
    },
  }

  beforeEach(() => {
    options = {
      props: { media: getAudioObj(overrides) },
      global: {
        stubs: ["VAudioThumbnail"],
        mocks: { route: { value: { name: "audio-id" } } },
      },
    }
  })

  it("renders the album title", async () => {
    await render(VMediaDetails, options)

    const album = screen.getByRole("link", { name: overrides.audio_set.title })
    expect(album).toHaveAttribute(
      "href",
      overrides.audio_set.foreign_landing_url
    )
  })

  it("hides the album title tag when it does not exists", async () => {
    options.props.media.audio_set = null
    await render(VMediaDetails, options)
    expect(screen.queryByText("Album")).toBeNull()
  })

  it("displays the main filetype when no alternative files are available", async () => {
    await render(VMediaDetails, options)
    expect(screen.queryByText("MP32")).toBeVisible()
  })

  it("displays multiple filetypes when they are available in alt_files", async () => {
    options.props.media.alt_files = [{ filetype: "wav" }, { filetype: "ogg" }]
    await render(VMediaDetails, options)
    expect(screen.queryByText("MP32, WAV, OGG")).toBeVisible()
  })

  it("displays only distinct filetypes", async () => {
    options.props.media.alt_files = [{ filetype: "ogg" }, { filetype: "ogg" }]
    await render(VMediaDetails, options)
    expect(screen.queryByText("MP32, OGG")).toBeVisible()
  })
})
