import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

const propsData = {
  images: [
    { id: "i1", url: "http://localhost:8080/i1.png", title: "image1" },
    { id: "i2", url: "http://localhost:8080/i2.jpg", title: "image2" },
    { id: "i3", url: "http://localhost:8080/i3.svg", title: "image3" },
  ],
  fetchState: {
    isSinglePage: true,
    isFetching: false,
    fetchingError: null,
  },
  isSinglePage: true,
  imageGridLabel: "Image Results",
}

describe("VImageGrid", () => {
  let options
  beforeEach(() => {
    options = {
      props: propsData,
      stubs: ["VLicense"],
    }
  })
  it("renders images without load more button for related images", () => {
    render(VImageGrid, options)
    expect(screen.queryAllByRole("img").length).toEqual(propsData.images.length)
    expect(screen.queryAllByRole("figure").length).toEqual(
      propsData.images.length
    )
    expect(screen.queryByTestId("load-more")).toBeNull()
  })
})
