import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VContentLink from "~/components/VContentLink/VContentLink.vue"

describe("VContentLink", () => {
  let options = {}

  beforeEach(() => {
    options = {
      props: { mediaType: "image", resultsCount: 123, to: "/images" },
    }
  })

  it("is enabled when there are results", () => {
    render(VContentLink, options)
    const btn = screen.getByRole("link")

    expect(btn).toHaveAttribute("href")
    expect(btn).not.toHaveAttribute("aria-disabled")
  })

  it("is disabled when there are no results", () => {
    options.props.resultsCount = 0
    render(VContentLink, options)
    const btn = screen.getByRole("link")

    expect(btn).not.toHaveAttribute("href")
    expect(btn).toHaveAttribute("aria-disabled")
    expect(btn.getAttribute("aria-disabled")).toBeTruthy()
  })
})
