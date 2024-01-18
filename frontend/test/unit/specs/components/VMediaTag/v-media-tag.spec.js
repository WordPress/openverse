import { RouterLinkStub } from "@vue/test-utils"
import { render, screen } from "@testing-library/vue"

import VMediaTag from "~/components/VMediaTag/VMediaTag.vue"

describe("VMediaTag", () => {
  let options = null

  beforeEach(() => {
    options = { props: {}, global: { stubs: {} } }
  })

  it("should render an span tag by default", async () => {
    const { container } = await render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("SPAN")
  })

  it("should render the supplied tag", async () => {
    options.props = {
      ...options.props,
      tag: "a",
      href: "https://example.com/",
    }

    const { container } = await render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("A")
    expect(container.firstChild.href).toEqual("https://example.com/")
  })

  it("should render the supplied Vue component", async () => {
    options.props = {
      ...options.props,
      tag: "RouterLink",
      to: "/",
    }
    options.global.stubs = {
      RouterLink: RouterLinkStub,
    }

    const { container } = await render(VMediaTag, options)
    expect(container.firstChild.tagName).toEqual("A")
  })

  it("renders slot content", async () => {
    const label = "I'm a label"
    options.slots = {
      default: () => `<div aria-label="${label}">Hello</div>`,
    }

    await render(VMediaTag, options)
    expect(screen.queryByLabelText(label)).toBeDefined()
  })
})
