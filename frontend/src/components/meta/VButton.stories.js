import { buttonForms, buttonSizes, buttonVariants } from "~/types/button"
import { capitalCase } from "~/utils/case"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

const buttonVariantGroups = {
  filled: buttonVariants.filter((variant) => variant.startsWith("filled-")),
  bordered: buttonVariants.filter((variant) => variant.startsWith("bordered-")),
  transparent: buttonVariants.filter((variant) =>
    variant.startsWith("transparent-")
  ),
}

const Template = (args) => ({
  template: `
    <div class="flex"><div id="wrapper"
        class="px-4 h-16 flex items-center justify-center"
        :class="variant.startsWith('transparent') ? 'bg-surface': 'bg-default'">
    <VButton :size="size" :variant="variant" v-bind="rest" class="description-bold" v-on="rest" href="/">
      Code is Poetry
    </VButton>
    </div></div>
  `,
  components: { VButton },
  setup() {
    const { size, variant, ...rest } = args
    return { size, variant, rest, args }
  },
})

const TemplateWithIcons = (args) => ({
  template: `
<div class="flex flex-col items-center gap-4 flex-wrap">
  <VButton :variant="args.variant" :size="args.size" :has-icon-start="true">
    <VIcon name="replay" />Button
  </VButton>
  <VButton :variant="args.variant" :size="args.size" has-icon-end>
    Button<VIcon name="external-link" />
  </VButton>
  <VButton :variant="args.variant" :size="args.size" has-icon-start has-icon-end>
    <VIcon name="replay" />Button<VIcon name="external-link" />
  </VButton>
</div>`,
  components: { VButton, VIcon },
  setup() {
    return { args }
  },
})

const VariantsTemplate = (args) => ({
  template: `
<div class="flex gap-4 flex-wrap">
  <VButton v-for="variant in variants"
           :variant="variant"
           :key="variant"
           class="description-bold"
           v-bind="buttonArgs">
    {{ capitalize(variant) }}
  </VButton>
  </div>`,
  components: { VButton },
  methods: {
    capitalize(str) {
      return capitalCase(str)
    },
  },
  setup() {
    const { variants, ...buttonArgs } = args
    return { variants, buttonArgs }
  },
})

export default {
  title: "Components/VButton",
  components: VButton,
  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
  args: {
    size: "medium",
  },
  argTypes: {
    as: {
      options: buttonForms,
      control: {
        type: "radio",
      },
    },

    variant: {
      options: buttonVariants,
    },

    pressed: {
      control: "boolean",
    },

    size: {
      options: buttonSizes,
      control: {
        type: "radio",
      },
    },

    disabled: {
      control: "boolean",
    },

    focusableWhenDisabled: {
      control: "boolean",
    },

    type: {
      control: "text",
    },

    click: {
      action: "click",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "VButton",

  args: {
    variant: "filled-pink-8",
  },
}

export const Filled = VariantsTemplate.bind({})
Filled.args = {
  variants: buttonVariantGroups.filled,
}

export const Bordered = {
  render: VariantsTemplate.bind({}),
  name: "bordered",

  args: {
    variants: buttonVariantGroups.bordered,
  },
}

export const Transparent = {
  render: VariantsTemplate.bind({}),
  name: "transparent",

  args: {
    variants: buttonVariantGroups.transparent,
  },
}

export const Icons = {
  render: TemplateWithIcons.bind({}),
  name: "icons",

  args: {
    variant: "bordered-dark",
  },

  argTypes: {
    pressed: { control: "boolean" },

    size: { options: buttonSizes, control: { type: "radio" } },

    variant: { options: buttonVariants },

    disabled: { control: "boolean" },
  },
}
