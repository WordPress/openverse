import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"

const media = [
  { id: "img1", url: "https://wp.org/img1.jpg" },
  { id: "img2", url: "https://wp.org/img2.jpg" },
]

describe("RelatedImage", () => {
  let props
  let options
  beforeEach(() => {
    props = { media, fetchState: { isFetching: false } }
    options = {
      propsData: props,
      stubs: ["VLicense"],
    }
  })
  it("should render an image grid", () => {
    render(VRelatedImages, options)

    expect(
      screen.getAllByRole("heading", { name: /related images/i })
    ).toHaveLength(1)
    expect(screen.queryAllByRole("heading").length).toEqual(3)
    expect(screen.queryAllByRole("img").length).toEqual(2)
    expect(screen.queryAllByRole("figure").length).toEqual(2)
  })

  it("should not render data when media array is empty", () => {
    options.propsData.media = []
    render(VRelatedImages, options)
    expect(screen.getByRole("heading").textContent).toContain("Related images")
    expect(screen.queryAllByRole("img").length).toEqual(0)
  })
})
