import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VScrollButton from "~/components/VScrollButton.vue"

describe("Scroll button", () => {
  it("should render a scroll button", async () => {
    const { container } = await render(VScrollButton, {
      global: { plugins: [i18n] },
    })
    expect(screen.getByRole("button")).toBeTruthy()
    expect(screen.getByLabelText(/scroll/i)).toBeTruthy()
    expect(container.querySelectorAll("svg").length).toEqual(1)
  })
})
