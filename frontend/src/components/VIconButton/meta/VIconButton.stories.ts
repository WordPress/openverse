import { h } from "vue"

import { baseButtonSizes, baseButtonVariants } from "#shared/types/button"
import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VIconButton",
  component: VIconButton,
  decorators: [WithScreenshotArea],

  argTypes: {
    size: {
      options: baseButtonSizes,
      control: "select",
    },

    variant: {
      options: baseButtonVariants,
      control: "select",
    },
  },
} satisfies Meta<typeof VIconButton>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VIconButton },
    setup() {
      return () => h(VIconButton, { ...args })
    },
  }),
  name: "Default",

  args: {
    variant: "filled-dark",
    size: "medium",
    label: "v-icon-button",

    iconProps: {
      name: "replay",
    },
  },
}

export const Sizes: Story = {
  render: (args) => ({
    components: { VIconButton },
    setup() {
      return () =>
        h(
          "div",
          { class: "flex gap-x-2" },
          baseButtonSizes.map((size) =>
            h("div", { class: "flex flex-col items-center p-2 gap-2" }, [
              h("p", { class: "label-bold" }, size),
              h(VIconButton, { ...args, size }, []),
            ])
          )
        )
    },
  }),
  name: "Sizes",

  args: {
    variant: "filled-dark",
    size: "small",
    label: "v-icon-button",

    iconProps: {
      name: "replay",
    },
  },
}
