import { RouterLinkStub } from "@vue/test-utils"
import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"

describe("VMediaTag", () => {
  let props = null
  let options = null

  beforeEach(() => {
    props = {}
    options = { propsData: props }
  })

  it("should render an span tag by default", () => {
    const { container } = render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("SPAN")
  })

  it("should render the supplied tag", () => {
    options.propsData = {
      ...options.propsData,
      tag: "a",
      href: "https://example.com/",
    }

    const { container } = render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("A")
    expect(container.firstChild.href).toEqual("https://example.com/")
  })

  it("should render the supplied Vue component", () => {
    options.propsData = {
      ...options.propsData,
      tag: "RouterLink",
      to: "/",
    }
    options.stubs = {
      RouterLink: RouterLinkStub,
    }

    const { container } = render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("A")
  })

  it("renders slot content", () => {
    const label = "I'm a label"
    options.slots = {
      default: `<div aria-label="${label}">Hello</div>`,
    }

    render(VMediaTag, options)
    expect(screen.queryByLabelText(label)).toBeDefined()
  })
})
