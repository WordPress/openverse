import { createApp, ref } from "vue"
import { render, screen } from "@testing-library/vue"
import { default as userEvent } from "@testing-library/user-event"

import { describe, expect, it } from "vitest"

import VItemGroup from "~/components/VItemGroup/VItemGroup.vue"
import VItem from "~/components/VItemGroup/VItem.vue"

const doFocus = (element) => {
  element.focus()
  return new Promise((r) => setTimeout(r, 0))
}

const TestWrapper = createApp({}).component("TestWrapper", {
  components: { VItemGroup, VItem },
  props: {
    hasDefaultSelection: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const items = new Array(4).fill(null).map((_, i) => ({
      id: i,
      label: `Item ${i}`,
    }))

    const selectedItem = ref(props.hasDefaultSelection ? items[0] : {})

    return { items, selectedItem }
  },
  template: `
    <div>
      <div>External element</div>
      <VItemGroup v-bind="$attrs">
        <VItem
          v-for="(item, idx) in items"
          :key="item.id"
          :selected="selectedItem.id === item.id"
          :is-first="idx === 0"
          @click="selectedItem = item"
        >
          {{ item.label }}
        </VItem>
      </VItemGroup>
    </div>
  `,
})._context.components.TestWrapper

describe("VItemGroup", () => {
  it("should render buttons with the appropriate roles", async () => {
    render(TestWrapper)
    expect(screen.queryByRole("menu")).toBeVisible()
    const items = screen.queryAllByRole("menuitemcheckbox")
    expect(items).toHaveLength(4)
    expect(items.every((item) => item.tagName === "BUTTON")).toBe(true)
  })

  it("should render functional buttons", async () => {
    const { container } = render(TestWrapper)
    const [, secondItem] = screen.queryAllByRole("menuitemcheckbox")
    expect(
      container.querySelector('[aria-pressed="true"][aria-checked="true"]')
    ).not.toBe(secondItem)
    await userEvent.click(secondItem)
    expect(
      container.querySelector('[aria-pressed="true"][aria-checked="true"]')
    ).toBe(secondItem)
  })

  it("should render a radio group", async () => {
    const { container } = render(TestWrapper, {
      attrs: { type: "radiogroup" },
    })
    expect(screen.queryByRole("radiogroup")).not.toBeNull()
    const [, secondItem] = screen.queryAllByRole("radio")
    expect(
      container.querySelector('[aria-pressed="true"][aria-checked="true"]')
    ).not.toBe(secondItem)
    await userEvent.click(secondItem)
    expect(
      container.querySelector('[aria-pressed="true"][aria-checked="true"]')
    ).toBe(secondItem)
  })

  describe("navigation", () => {
    it("should render the first item tabbable when there is no default selection and none are selected", async () => {
      const { container } = render(TestWrapper, {
        props: { hasDefaultSelection: false },
        attrs: { type: "radiogroup" },
      })
      const tabbableElements = container.querySelectorAll('[tabindex="0"]')
      expect(tabbableElements).toHaveLength(1)
      const [tabbableElement] = tabbableElements
      expect(tabbableElement).toBe(screen.queryAllByRole("radio")[0])
    })

    it("should render all items tabbable when in a menu", async () => {
      const { container } = render(TestWrapper, {
        attrs: { type: "menu" },
      })
      const tabbableElements = container.querySelectorAll('[tabindex="0"]')
      const items = screen.queryAllByRole("menuitemcheckbox")
      items.forEach((item) => expect(tabbableElements).toContain(item))
    })

    it("should render only the selected item as tabbable", async () => {
      const { container } = render(TestWrapper, {
        attrs: { type: "radiogroup" },
        props: { hasDefaultSelection: false },
      })
      const [, secondItem] = screen.queryAllByRole("radio")
      await userEvent.click(secondItem)
      // Focus off the clicked item and outside the group so that the group does not have focus but there is still a selected item
      await doFocus(screen.getByText(/external element/i))
      const tabbableElements = container.querySelectorAll('[tabindex="0"]')
      expect(tabbableElements).toHaveLength(1)
      const [tabbableElement] = tabbableElements
      expect(tabbableElement).toBe(secondItem)
    })

    it("should render the currently focused item as tabbable even when there is a selection", async () => {
      const { container } = render(TestWrapper, {
        attrs: { type: "radiogroup" },
      })
      const [, secondItem] = screen.queryAllByRole("radio")
      await doFocus(secondItem)
      const tabbableElements = container.querySelectorAll('[tabindex="0"]')
      expect(tabbableElements).toHaveLength(1)
      const [tabbableElement] = tabbableElements
      expect(tabbableElement).toBe(secondItem)
    })

    describe("arrow keys", () => {
      it.each(["ArrowUp", "ArrowLeft"])(
        "should focus to the previous item on %s",
        async (key) => {
          render(TestWrapper, { attrs: { type: "radiogroup" } })
          const [firstItem, secondItem] = screen.queryAllByRole("radio")

          await doFocus(secondItem)
          await userEvent.keyboard(`{${key}}`)
          expect(firstItem).toHaveFocus()
        }
      )

      it.each(["ArrowUp", "ArrowLeft"])(
        "should go to the last item when on the first item and pressing %s",
        async (key) => {
          render(TestWrapper, { attrs: { type: "radiogroup" } })
          const [firstItem, , , lastItem] = screen.queryAllByRole("radio")
          await doFocus(firstItem)
          await userEvent.keyboard(`{${key}}`)
          expect(lastItem).toHaveFocus()
        }
      )

      it.each(["ArrowDown", "ArrowRight"])(
        "should focus to the next item on %s",
        async (key) => {
          render(TestWrapper, { attrs: { type: "radiogroup" } })
          const [firstItem, secondItem] = screen.queryAllByRole("radio")

          await doFocus(firstItem)
          await userEvent.keyboard(`{${key}}`)
          expect(secondItem).toHaveFocus()
        }
      )

      it.each(["ArrowDown", "ArrowRight"])(
        "should go to the first item when on the last item and pressing %s",
        async (key) => {
          render(TestWrapper, { attrs: { type: "radiogroup" } })
          const [firstItem, , , lastItem] = screen.queryAllByRole("radio")

          await doFocus(lastItem)
          await userEvent.keyboard(`{${key}}`)
          expect(firstItem).toHaveFocus()
        }
      )

      describe("rtl", () => {
        describe("vertical", () => {
          it.each(["ArrowUp", "ArrowLeft"])(
            "should focus to the previous item on %s",
            async (key) => {
              render(TestWrapper, { attrs: { type: "radiogroup" } })
              const [firstItem, secondItem] = screen.queryAllByRole("radio")

              await doFocus(secondItem)
              await userEvent.keyboard(`{${key}}`)
              expect(firstItem).toHaveFocus()
            }
          )

          it.each(["ArrowUp", "ArrowLeft"])(
            "should go to the last item when on the first item and pressing %s",
            async (key) => {
              render(TestWrapper, { attrs: { type: "radiogroup" } })
              const [firstItem, , , lastItem] = screen.queryAllByRole("radio")
              await doFocus(firstItem)
              await userEvent.keyboard(`{${key}}`)
              expect(lastItem).toHaveFocus()
            }
          )

          it.each(["ArrowDown", "ArrowRight"])(
            "should focus to the next item on %s",
            async (key) => {
              render(TestWrapper, { attrs: { type: "radiogroup" } })
              const [firstItem, secondItem] = screen.queryAllByRole("radio")

              await doFocus(firstItem)
              await userEvent.keyboard(`{${key}}`)
              expect(secondItem).toHaveFocus()
            }
          )

          it.each(["ArrowDown", "ArrowRight"])(
            "should go to the first item when on the last item and pressing %s",
            async (key) => {
              render(TestWrapper, { attrs: { type: "radiogroup" } })
              const [firstItem, , , lastItem] = screen.queryAllByRole("radio")

              await doFocus(lastItem)
              await userEvent.keyboard(`{${key}}`)
              expect(firstItem).toHaveFocus()
            }
          )
        })

        describe("horizontal", () => {
          // TODO: Mock direction and add ArrowRight tests
          it.each(["ArrowUp"])(
            "should focus to the previous item on %s",
            async (key) => {
              render(TestWrapper, {
                attrs: { type: "radiogroup", direction: "horizontal" },
              })
              const [firstItem, secondItem] = screen.queryAllByRole("radio")

              await doFocus(secondItem)
              await userEvent.keyboard(`{${key}}`)
              expect(firstItem).toHaveFocus()
            }
          )

          // TODO: Mock direction and add ArrowRight tests
          it.each(["ArrowUp"])(
            "should go to the last item when on the first item and pressing %s",
            async (key) => {
              render(TestWrapper, {
                attrs: { type: "radiogroup", direction: "horizontal" },
              })
              const [firstItem, , , lastItem] = screen.queryAllByRole("radio")
              await doFocus(firstItem)
              await userEvent.keyboard(`{${key}}`)
              expect(lastItem).toHaveFocus()
            }
          )

          // TODO: Mock direction and add ArrowRight tests
          it.each(["ArrowDown"])(
            "should focus to the next item on %s",
            async (key) => {
              render(TestWrapper, {
                attrs: { type: "radiogroup", direction: "horizontal" },
              })
              const [firstItem, secondItem] = screen.queryAllByRole("radio")

              await doFocus(firstItem)
              await userEvent.keyboard(`{${key}}`)
              expect(secondItem).toHaveFocus()
            }
          )

          // TODO: Mock direction and add ArrowRight tests
          it.each(["ArrowDown"])(
            "should go to the first item when on the last item and pressing %s",
            async (key) => {
              render(TestWrapper, {
                attrs: { type: "radiogroup", direction: "horizontal" },
              })
              const [firstItem, , , lastItem] = screen.queryAllByRole("radio")

              await doFocus(lastItem)
              await userEvent.keyboard(`{${key}}`)
              expect(firstItem).toHaveFocus()
            }
          )
        })
      })
    })
  })
})
