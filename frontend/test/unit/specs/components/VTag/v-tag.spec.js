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

  // https://github.com/wordpress/openverse/issues/411
  it.skip("renders slot content", async () => {
    const slotText = "Slot test"
    options.slots = { default: () => `<div>${slotText}</div>` }

    await render(VTag, options)
    expect(screen.getByText(slotText)).toBeDefined()
  })
})
