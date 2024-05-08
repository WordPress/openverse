import { baseButtonSizes, baseButtonVariants } from "~/types/button"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

const Template = (args) => ({
  template: `
    <VIconButton :size="args.size" :variant="args.variant" v-bind="args" v-on="args" label="v-icon-button" />
  `,
  components: { VIconButton },
  setup() {
    return { args }
  },
})

const sizesTemplate = (args) => ({
  template: `
    <div class="flex gap-x-2">
      <div v-for="size in args.baseButtonSizes" :key="size" class="flex flex-col items-center p-2 gap-2">
        <p class="label-bold">{{ size }}</p>
        <VIconButton
           label="v-icon-button"
           :size="size"
           :variant="args.variant"
           v-bind="args"
           v-on="args"
        />
      </div>
    </div>
  `,
  components: { VIconButton },
  setup() {
    args.baseButtonSizes = baseButtonSizes
    return { args }
  },
})

export default {
  title: "Components/VIconButton",
  component: VIconButton,

  argTypes: {
    size: {
      options: baseButtonSizes,
      control: "select",
    },

    variant: {
      options: baseButtonVariants,
      control: "select",
    },

    click: {
      action: "click",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    variant: "filled-dark",
    size: "medium",

    iconProps: {
      name: "replay",
    },
  },
}

export const Sizes = {
  render: sizesTemplate.bind({}),
  name: "Sizes",

  args: {
    variant: "filled-dark",
    size: "small",

    iconProps: {
      name: "replay",
    },
  },
}
