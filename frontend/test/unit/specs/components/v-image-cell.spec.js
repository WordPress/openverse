import { render } from "@testing-library/vue"

import { createApp } from "vue"

import { image } from "~~/test/unit/fixtures/image"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

const RouterLinkStub = createApp({}).component("RouterLink", {
  template: "<a :href='href'><slot /></a>",
  props: ["to"],
  computed: {
    href() {
      return this.to
    },
  },
})._context.components.RouterLink
describe("VImageCell", () => {
  let options = {}

  beforeEach(() => {
    options = {
      global: {
        plugins: [i18n],
        stubs: {
          RouterLink: RouterLinkStub,
        },
      },
      props: {
        image,
        searchTerm: "cat",
        relatedTo: null,
      },
    }
  })

  it("is blurred when the image is sensitive", async () => {
    options.props.image.isSensitive = true
    const { getByAltText } = render(VImageCell, options)
    const img = getByAltText("This image may contain sensitive content.")
    expect(img).toHaveClass("blur-image")
  })

  it("is does not contain title anywhere when the image is sensitive", async () => {
    options.props.image.isSensitive = true
    const screen = render(VImageCell, options)
    let match = RegExp(image.title)
    expect(screen.queryAllByText(match)).toEqual([])
    expect(screen.queryAllByTitle(match)).toEqual([])
    expect(screen.queryAllByAltText(match)).toEqual([])
  })
})
