import { h } from "vue"

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

export default {
  title: "Components/VButton",
  component: VButton,
  parameters: {
    viewport: {
      defaultViewport: "sm",
    },
  },
  args: {
    size: "medium",
  },
  argTypes: {
    as: { options: buttonForms, control: { type: "radio" } },

    variant: { options: buttonVariants, control: { type: "select" } },

    pressed: { control: "boolean" },

    size: { options: buttonSizes, control: { type: "select" } },

    disabled: { control: "boolean" },

    focusableWhenDisabled: { control: "boolean" },

    type: { control: "text" },

    onClick: { action: "click" },
    onMouseDown: { action: "mousedown" },
    onKeydown: { action: "keydown" },
    onFocus: { action: "focus" },
    onBlur: { action: "blur" },
  },
}

const Template = (args) => ({
  components: { VButton },
  setup() {
    const { size, variant, ...rest } = args
    return () =>
      h("div", { class: "flex" }, [
        h(
          "div",
          {
            id: "wrapper",
            class: [
              "px-4 h-16 flex items-center justify-center",
              variant.startsWith("transparent") ? "bg-surface" : "bg-default",
            ],
          },
          [
            h(
              VButton,
              {
                size,
                variant,
                class: "description-bold",
                href: "/",
                ...rest,
              },
              () => "Code is Poetry"
            ),
          ]
        ),
      ])
  },
})

const TemplateWithIcons = (args) => ({
  components: { VButton, VIcon },
  setup() {
    return () =>
      h("div", { class: "flex flex-col items-center gap-4 flex-wrap" }, [
        h(
          VButton,
          { variant: args.variant, size: args.size, "has-icon-start": true },
          () => [h(VIcon, { name: "replay" }), "Button"]
        ),
        h(
          VButton,
          { variant: args.variant, size: args.size, "has-icon-end": true },
          () => ["Button", h(VIcon, { name: "external-link" })]
        ),
        h(
          VButton,
          {
            variant: args.variant,
            size: args.size,
            "has-icon-start": true,
            "has-icon-end": true,
          },
          () => [
            h(VIcon, { name: "replay" }),
            "Button",
            h(VIcon, { name: "external-link" }),
          ]
        ),
      ])
  },
})

const VariantsTemplate = (args) => ({
  components: { VButton },
  setup() {
    const { variants, ...buttonArgs } = args
    return () =>
      h(
        "div",
        { class: "flex gap-4 flex-wrap" },
        variants.map((variant) =>
          h(
            VButton,
            {
              variant,
              key: variant,
              class: "description-bold",
              ...buttonArgs,
            },
            () => capitalCase(variant)
          )
        )
      )
  },
})

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
