import { screen } from "@testing-library/vue"

import { beforeEach, describe, expect, it, vi } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import { useMatchHomeRoute } from "~/composables/use-match-routes"

import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"
import { FIELD_SIZES } from "~/components/VInputField/VInputField.vue"

vi.mock("~/composables/use-match-routes", () => ({
  useMatchHomeRoute: vi.fn(),
}))

const sizes = Object.keys(FIELD_SIZES)
const defaultPlaceholder = "Enter search query"

describe("VSearchBar", () => {
  let options
  beforeEach(() => {
    options = {
      props: { placeholder: defaultPlaceholder, size: "medium" },
      stubs: { ClientOnly: true },
    }
  })

  it.each(sizes)(
    'renders an input field with placeholder and type="search" (%s size)',
    async (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      await render(VSearchBar, options)

      const inputElement = screen.getByPlaceholderText(defaultPlaceholder)

      expect(inputElement.tagName).toBe("INPUT")
      expect(inputElement).toHaveAttribute("type", "search")
      expect(inputElement).toHaveAttribute("placeholder", defaultPlaceholder)
    }
  )

  it.each(sizes)(
    'renders a button with type="submit", ARIA label and SR text (%s size)',
    async (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      await render(VSearchBar, options)

      const btnElement = screen.getByRole("button", { name: /search/i })

      expect(btnElement.tagName).toBe("BUTTON")
      expect(btnElement).toHaveAttribute("type", "submit")
      expect(btnElement).toHaveAttribute("aria-label", "Search")
    }
  )

  describe("placeholder", () => {
    it("should default to hero.search.placeholder", async () => {
      delete options.props.placeholder

      await render(VSearchBar, options)
      expect(
        screen.queryByPlaceholderText(/Search for content/i)
      ).not.toBeNull()
    })

    it("should use the prop when provided", async () => {
      const placeholder = "This is a different placeholder from the default"
      options.props.placeholder = placeholder
      await render(VSearchBar, options)
      expect(screen.queryByPlaceholderText(placeholder)).not.toBeNull()
    })
  })
})
