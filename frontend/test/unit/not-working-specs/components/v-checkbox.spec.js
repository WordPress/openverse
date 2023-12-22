import Vue from "vue"
import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VCheckbox from "~/components/VCheckbox/VCheckbox.vue"

const TestWrapperStringLabel = ({
  id = "simple",
  value = "simple",
  checked = false,
  defaultSlot = "JPGs",
  disabled = false,
} = {}) => {
  // eslint-disable-next-line vue/one-component-per-file
  return Vue.component("TestWrapper", {
    components: { VCheckbox },
    data() {
      return { checked, status: "" }
    },
    computed: {
      attrs() {
        return {
          id: id,
          value: value,
          checked: this.checked,
          defaultSlot: defaultSlot,
          disabled: disabled,
        }
      },
    },
    methods: {
      updateStatus(params) {
        this.status = Object.values(params).join(",")
      },
    },
    template: `<div><span>{{status}}</span><VCheckbox v-bind="attrs" @change="updateStatus">${defaultSlot}</VCheckbox></div>`,
  })
}

describe("VCheckbox", () => {
  it("should render a checkbox with a string label", async () => {
    const wrapper = TestWrapperStringLabel()
    const { container } = await render(wrapper)
    // Finding a checked input doesn't work using { checked: false/true }
    // does not change the result, the checkbox is still returned.
    // toHaveAttribute('checked', 'true') also doesn't work, screen.debug()
    // returns an element without `checked` attribute, although the attribute
    // exists in the app/Storybook.
    const checkboxes = screen.queryAllByLabelText(/jpgs/i, { role: "checkbox" })

    // The checkmark svg should not be visible
    expect(container.querySelector("svg")).not.toBeVisible()
    expect(checkboxes).toHaveLength(1)
  })

  it("should render a checked checkbox if `checked` is true", async () => {
    const wrapper = TestWrapperStringLabel({ checked: true })
    const { container } = await render(wrapper)
    const checkboxes = screen.queryAllByLabelText(/jpgs/i, { role: "checkbox" })

    // The checkmark svg should be visible
    expect(container.querySelector("svg")).toBeVisible()
    expect(checkboxes).toHaveLength(1)
  })

  it("should emit event on change", async () => {
    const wrapper = TestWrapperStringLabel()
    const { container } = await render(wrapper)
    await fireEvent.click(screen.queryByRole("checkbox"))

    // Testing the method that handles the emitted data instead of testing emitted event
    expect(container.querySelector("span").textContent).toBe(
      "simple,simple,true"
    )
  })

  it("should render a disabled checkbox if `disabled` is true", async () => {
    const wrapper = TestWrapperStringLabel({ disabled: true })
    await render(wrapper)
    const checkboxes = screen.queryAllByLabelText(/jpgs/i, { role: "checkbox" })

    expect(checkboxes).toHaveLength(1)
    expect(checkboxes[0]).toHaveAttribute("disabled", "disabled")
  })
})
