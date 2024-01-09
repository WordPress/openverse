// @vitest-environment jsdom

import { describe, expect, it, vi } from "vitest"

import { render, screen } from "@testing-library/vue"

import { useReducedMotion } from "~/composables/use-reduced-motion"

import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"

vi.mock("~/utils/console", () => ({
  warn: vi.fn(),
  log: vi.fn(),
}))

vi.mock("~/composables/use-reduced-motion", () => ({
  useReducedMotion: vi.fn(),
}))

describe("VLogoLoader", () => {
  it("should render the logo", async () => {
    render(VLogoLoader)
    const element = screen.getByTestId("logo-loader")
    expect(element).toBeInTheDocument()
  })

  describe("accessibility", () => {
    it("should render differently when the user prefers reduced motion", async () => {
      useReducedMotion.mockImplementation(() => true)

      render(VLogoLoader, {
        props: { status: "loading" },
      })
      const element = screen.getByTestId("logo-loader")
      expect(element).toHaveAttribute("data-prefers-reduced-motion", "true")
    })
    it("should show the default loading style when no motion preference is set", async () => {
      useReducedMotion.mockImplementation(() => false)

      render(VLogoLoader, {
        props: { status: "loading" },
      })
      const element = screen.getByTestId("logo-loader")
      expect(element).not.toHaveAttribute("data-prefers-reduced-motion")
    })
  })
})
