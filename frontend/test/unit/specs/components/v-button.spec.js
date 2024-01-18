import { screen } from "@testing-library/vue"

import { describe, expect, it } from "vitest"

import { nextTick } from "vue"

import { render } from "~~/test/unit/test-utils/render"

import VButton from "~/components/VButton.vue"

/**
 * Throughout this suite we use the `screen.findBy*` functions to asynchronously
 * wait for the component to re-render. There might be some kind of performance
 * problem with the component's implementation, but if we don't "wait" for it
 * to settle, then all the props that are changed after `onMounted` completes
 * won't be rendered.
 */
describe("VButton", () => {
  it('should render a `button` by default with type="button" and no tabindex', async () => {
    await render(VButton, {
      props: { variant: "filled-white", size: "medium" },
      slots: { default: () => "Code is Poetry" },
    })

    const element = await screen.findByRole("button")

    expect(element.tagName).toBe("BUTTON")
    expect(element).toHaveAttribute("type", "button")
    expect(element).not.toHaveAttribute("tabindex")
  })

  it("should allow passing an explicit type", async () => {
    await render(VButton, {
      props: { type: "submit", variant: "filled-white", size: "medium" },
      slots: { default: () => "Code is Poetry" },
    })

    const element = await screen.findByRole("button")

    expect(element).toHaveAttribute("type", "submit")
  })

  it("should render an anchor with no type attribute", async () => {
    await render(VButton, {
      attrs: { href: "http://localhost" },
      props: { as: "VLink", variant: "filled-white", size: "medium" },
      slots: { default: () => "Code is Poetry" },
    })
    await nextTick()

    const element = await screen.findByText(/code is poetry/i)

    expect(element.tagName).toBe("A")
    expect(element).not.toHaveAttribute("type")
  })

  it("should render the disabled attribute on a button when the element is explicitly unfocusableWhenDisabled and is disabled", async () => {
    await render(VButton, {
      props: {
        disabled: true,
        focusableWhenDisabled: false,
        variant: "filled-white",
        size: "medium",
      },
      slots: { default: () => "Code is Poetry" },
    })

    const element = await screen.findByRole("button")

    expect(element).toHaveAttribute("disabled")
  })

  it("should not render the disabled attribute if the element is focusableWhenDisabled", async () => {
    await render(VButton, {
      props: {
        disabled: true,
        focusableWhenDisabled: true,
        variant: "filled-white",
        size: "medium",
      },
      slots: { default: () => "Code is Poetry" },
    })

    const element = await screen.findByRole("button")

    expect(element).not.toHaveAttribute("disabled")
    expect(element).toHaveAttribute("aria-disabled", "true")
  })

  it("should not render the disabled attribute on elements that do not support it", async () => {
    await render(VButton, {
      props: {
        as: "VLink",
        disabled: true,
        focusableWhenDisabled: true,
        href: "https://wordpress.org",
        variant: "filled-white",
        size: "medium",
      },
      slots: { default: () => "Code is Poetry" },
    })

    const element = await screen.findByText(/code is poetry/i)

    expect(element).not.toHaveAttribute("disabled")
    expect(element).toHaveAttribute("aria-disabled", "true")
  })
})
