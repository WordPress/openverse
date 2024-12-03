import { screen } from "@testing-library/vue"
import { render } from "~~/test/unit/test-utils/render"

import VTag from "~/components/VTag/VTag.vue"

describe("VTag", () => {
  let options = {}

  beforeEach(() => {
    options = {
      props: { href: "https://example.com/" },
      slots: { default: () => "Hello" },
    }
  })

  it("should render an anchor tag by default", async () => {
    const { getByRole } = await render(VTag, options)
    const link = getByRole("link", { name: "Hello" })
    expect(link).toBeDefined()
    expect(link.href).toEqual("https://example.com/")
  })

  it("renders slot content", async () => {
    const slotText = "Slot test"
    // Using a non-function value for the slot causes a Vue warning,
    // but a function value is not rendered correctly by the unit tests.
    options.slots = { default: `<div>${slotText}</div>` }

    await render(VTag, options)
    expect(screen.getByText(slotText)).toBeDefined()
  })
})
