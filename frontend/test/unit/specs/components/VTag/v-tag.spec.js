import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VTag from "~/components/VTag/VTag.vue"

describe("VTag", () => {
  let options = {}

  beforeEach(() => {
    options = {
      props: { href: "https://example.com/" },
      slots: { default: "Hello" },
    }
  })

  it("should render an anchor tag by default", () => {
    const { getByRole } = render(VTag, options)
    const link = getByRole("link", { name: "Hello" })
    expect(link).toBeDefined()
    expect(link.href).toEqual("https://example.com/")
  })

  it("renders slot content", () => {
    const slotText = "Slot test"
    options.slots = { default: `<div>${slotText}</div>` }

    render(VTag, options)
    expect(screen.getByText(slotText)).toBeDefined()
  })
})
