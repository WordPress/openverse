import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VTag from "~/components/VTag/VTag.vue"


describe("VTag", () => {
  let props = null
  let options = null

  beforeEach(() => {
    props = {}
    options = { propsData: props }
  })

  it("should render an anchor tag by default", () => {
    options.propsData = {
        ...options.propsData,
        title: "exTitle",
        href: "https://example.com/",
      }
    const { container } = render(VTag, options)
    expect(container.firstChild.tagName).toEqual("A")
  })

  it("should pass all props to VButton", () => {
    options.propsData = {
        ...options.propsData,
        title: "exTitle",
        href: "https://example.com/",
      }
    const { container } = render(VTag, options)
    expect(container.firstChild.title).toEqual("exTitle")
    expect(container.firstChild.href).toEqual("https://example.com/")
  })

  it("renders slot content", () => {
    const label = "I'm a label"
    options.propsData = {
        href: "https://example.com/",
        title: "Slot test",
    }
    options.slots = {
      default: `<div aria-label="${label}">Hello</div>`,
    }

    render(VTag, options)
    expect(screen.queryByLabelText(label)).toBeDefined()
  })
})
