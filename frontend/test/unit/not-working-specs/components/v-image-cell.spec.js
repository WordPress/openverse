import { beforeEach, describe, it } from "vitest"

import { render } from "~~/test/unit/test-utils/render"
import { image } from "~~/test/unit/fixtures/image"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

describe("VImageCell", () => {
  let options = {}

  beforeEach(() => {
    options = {
      props: {
        image,
        searchTerm: "cat",
        relatedTo: null,
      },
    }
  })

  it("is blurred when the image is sensitive", async () => {
    options.props.image.isSensitive = true
    const { getByAltText } = await render(VImageCell, options)
    const img = getByAltText("This image may contain sensitive content.")
    expect(img).toHaveClass("blur-image")
  })

  it("is does not contain title anywhere when the image is sensitive", async () => {
    options.props.image.isSensitive = true
    const screen = await render(VImageCell, options)
    let match = RegExp(image.title)
    expect(screen.queryAllByText(match)).toEqual([])
    expect(screen.queryAllByTitle(match)).toEqual([])
    expect(screen.queryAllByAltText(match)).toEqual([])
  })
})
