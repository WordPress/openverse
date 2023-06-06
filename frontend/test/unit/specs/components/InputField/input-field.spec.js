import { screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import VInputField from "~/components/VInputField/VInputField.vue"

const props = {
  fieldId: "input-id",
  labelText: "Label",
  size: "medium",
}

describe("VInputField", () => {
  it('should render an `input` element with type="text"', () => {
    render(VInputField, {
      attrs: {
        placeholder: "Enter some text",
      },
      propsData: props,
    })
    const element = screen.getByPlaceholderText("Enter some text")

    expect(element.tagName).toBe("INPUT")
    expect(element).toHaveAttribute("type", "text")
  })

  it("should allow changing the type", () => {
    render(VInputField, {
      attrs: {
        placeholder: "Enter some number",
        type: "number",
      },
      propsData: props,
    })
    const element = screen.getByPlaceholderText("Enter some number")

    expect(element).toHaveAttribute("type", "number")
  })

  it("should set the ID on the `input` to allow attaching labels", () => {
    render(VInputField, {
      attrs: {
        placeholder: "Enter some text",
      },
      propsData: props,
    })

    const element = screen.getByPlaceholderText("Enter some text")

    expect(element).toHaveAttribute("id", "input-id")
  })

  it("should render the label text connected to the input field if specified", () => {
    render(VInputField, {
      propsData: props,
    })

    const element = screen.getByLabelText("Label")

    expect(element.tagName).toBe("INPUT")
  })
})
