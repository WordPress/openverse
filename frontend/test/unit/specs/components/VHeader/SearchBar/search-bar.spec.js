import { render, screen } from "@testing-library/vue"

import { createPinia, PiniaVuePlugin } from "~~/test/unit/test-utils/pinia"

import { useMatchHomeRoute } from "~/composables/use-match-routes"

import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"

jest.mock("~/composables/use-match-routes", () => ({
  useMatchHomeRoute: jest.fn(),
}))

const sizes = ["small", "medium", "large", "standalone"]
const defaultPlaceholder = "Enter search query"

const configureVue = (vue) => {
  vue.use(PiniaVuePlugin)
  return {
    pinia: createPinia(),
  }
}

describe("VSearchBar", () => {
  let options
  beforeEach(() => {
    options = {
      props: { placeholder: defaultPlaceholder, size: "standalone" },
      stubs: { ClientOnly: true },
      mocks: {
        $nuxt: {
          context: {
            app: { $ua: {} },
          },
        },
      },
    }
  })

  it.each(sizes)(
    'renders an input field with placeholder and type="search" (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      render(VSearchBar, options, configureVue)

      const inputElement = screen.getByPlaceholderText(defaultPlaceholder)

      expect(inputElement.tagName).toBe("INPUT")
      expect(inputElement).toHaveAttribute("type", "search")
      expect(inputElement).toHaveAttribute("placeholder", defaultPlaceholder)
    }
  )

  it.each(sizes)(
    'renders a button with type="submit", ARIA label and SR text (%s size)',
    (size) => {
      useMatchHomeRoute.mockImplementation(() => false)
      options.props.size = size
      render(VSearchBar, options, configureVue)

      const btnElement = screen.getByLabelText("search.search")

      expect(btnElement.tagName).toBe("BUTTON")
      expect(btnElement).toHaveAttribute("type", "submit")
      expect(btnElement).toHaveAttribute("aria-label", "search.search")
    }
  )

  describe("placeholder", () => {
    it("should default to hero.search.placeholder", () => {
      delete options.props.placeholder

      render(VSearchBar, options, configureVue)
      expect(
        screen.queryByPlaceholderText("hero.search.placeholder")
      ).not.toBeNull()
    })

    it("should use the prop when provided", () => {
      const placeholder = "This is a different placeholder from the default"
      options.props.placeholder = placeholder
      render(VSearchBar, options, configureVue)
      expect(screen.queryByPlaceholderText(placeholder)).not.toBeNull()
    })
  })
})
