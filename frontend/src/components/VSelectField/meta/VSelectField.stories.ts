import { h, ref } from "vue"

import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VIcon from "~/components/VIcon/VIcon.vue"
import VSelectField from "~/components/VSelectField/VSelectField.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const baseArgs = {
  fieldId: "fruit",
  blankText: "Fruit",
  labelText: "Fruit",
  choices: [
    { key: "a", text: "Apple" },
    { key: "b", text: "Banana" },
    { key: "c", text: "Cantaloupe" },
  ],
}

const meta = {
  title: "Components/VSelectField",
  component: VSelectField,
  decorators: [WithScreenshotArea],

  argTypes: {
    "onUpdate:modelValue": {
      action: "update:modelValue",
    },
  },
} satisfies Meta<typeof VSelectField>

export default meta
type Story = StoryObj<typeof meta>

const Template: Story = {
  render: (args) => ({
    components: { VSelectField },
    setup() {
      return () => h(VSelectField, args)
    },
  }),
  args: {} as Story["args"],
}

export const Default = {
  ...Template,
  name: "Default",
  args: baseArgs,
}

export const WithoutBorder = {
  ...Template,
  name: "Without border",

  args: {
    ...baseArgs,
    variant: "borderless",
  },
}

export const VModel: Story = {
  render: (args) => ({
    components: { VSelectField },
    setup() {
      const choice = ref("a")
      return () =>
        h("div", [
          h(VSelectField, { ...args, modelValue: choice.value }),
          choice.value,
        ])
    },
  }),
  name: "v-model",
  args: baseArgs,
}

export const WithIcon: Story = {
  render: (args) => ({
    components: { VSelectField, VIcon },
    setup() {
      return () =>
        h(VSelectField, args, { start: () => h(VIcon, { name: "radiomark" }) })
    },
  }),
  name: "With icon",
  args: baseArgs,
}

export const WithConstraints: Story = {
  render: (args) => ({
    components: { VSelectField, VIcon },
    setup() {
      return () =>
        h(
          VSelectField,
          { ...args, class: "max-w-[100px]" },
          { start: () => h(VIcon, { name: "radiomark" }) }
        )
    },
  }),
  name: "With constraints",

  args: {
    ...baseArgs,

    choices: [
      {
        key: "short",
        text: "Kiwi",
      },
      {
        key: "long",
        text: "Bob Gordon American Elderberry",
      },
    ],
  },
}
