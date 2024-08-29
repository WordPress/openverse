import { h, ref } from "vue"

import VRadio from "~/components/VRadio/VRadio.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VRadio",
  component: VRadio,

  argTypes: {
    onChange: { action: "change" },
  },
} satisfies Meta<typeof VRadio> & { argTypes: { onChange: { action: string } } }

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VRadio },
    setup() {
      return () =>
        h("div", h(VRadio, { ...args }, { default: () => "Label text" }))
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",

  // if same as value, radio is checked
  args: {
    id: "default",
    value: "value",
    modelValue: "modelValue",
  },
}

export const Disabled = {
  ...Template,
  name: "Disabled",

  args: {
    id: "disabled",
    value: "value",
    modelValue: "modelValue",
    disabled: true,
  },
}

export const VModel: Story = {
  render: (args) => ({
    components: { VRadio },
    setup() {
      const picked = ref<string>(args.value)
      return () =>
        h(
          "div",
          h("form", { class: "flex flex-col gap-2 mb-2" }, [
            h(
              VRadio,
              { id: "a", name: "test", value: "A", modelValue: picked.value },
              { default: () => "A" }
            ),
            h(
              VRadio,
              { id: "b", name: "test", value: "B", modelValue: picked.value },
              { default: () => "B" }
            ),
          ])
        )
    },
  }),
  name: "v-model",
  args: {
    id: "a",
    value: "A",
  },
}
