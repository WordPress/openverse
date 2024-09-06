import { h, ref } from "vue"

import VInputField from "~/components/VInputField/VInputField.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VInputField",
  component: VInputField,

  argTypes: {
    "onUpdate:modelValue": {
      action: "update:modelValue",
    },
  },
  args: {
    fieldId: "field",
    labelText: "Label",
  },
} satisfies Meta<typeof VInputField>
export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VInputField },
    setup() {
      return () =>
        h(
          VInputField,
          { ...args },
          {
            default: () =>
              h("span", { class: "whitespace-nowrap me-2" }, "Extra info"),
          }
        )
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",

  args: {
    value: "Text goes here",
  },
}

export const VModel: Story = {
  render: (args) => ({
    components: { VInputField },
    setup() {
      const text = ref("Hello, World!")
      const updateText = (value: unknown) =>
        (text.value = typeof value === "string" ? value : "")
      return () =>
        h(
          "div",
          {},
          h(
            VInputField,
            {
              ...args,
              modelValue: text.value,
              "onUpdate:modelValue": updateText,
            },
            { default: () => text.value }
          )
        )
    },
  }),
  name: "v-model",
}

export const WithPlaceholder: Story = {
  ...Template,
  name: "With placeholder",

  args: {
    placeholder: "Enter something here",
  },
}

export const WithLabelText: Story = {
  ...Template,
  name: "With label text",

  args: {
    labelText: "Label:",
  },
}

export const WithCustomLabel: Story = {
  render: (args) => ({
    components: { VInputField },
    setup() {
      return () =>
        h("div", {}, [
          h("label", { for: "field" }, "Label:"),
          h(VInputField, { ...args }),
        ])
    },
  }),
  name: "With custom label",
}

export const WithConnections: Story = {
  ...Template,
  name: "With connections",

  args: {
    connectionSides: ["start", "end"],
  },
}
