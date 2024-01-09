import { render, screen } from "@testing-library/vue"

import { i18n } from "~~/test/unit/test-utils/i18n"

import VScrollButton from "~/components/VScrollButton.vue"

describe("Scroll button", () => {
  it("should render a scroll button", () => {
    const { container } = render(VScrollButton, { global: { plugins: [i18n] } })
    expect(screen.getByRole("button")).toBeTruthy()
    expect(screen.getByLabelText(/scroll/i)).toBeTruthy()
    expect(container.querySelectorAll("svg").length).toEqual(1)
  })
})
