import { h } from "vue"

import { capitalCase } from "#shared/utils/case"
import { buttonForms, buttonSizes, buttonVariants } from "#shared/types/button"

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
    sSize: "medium",
  },
  argTypes: {
    as: { options: buttonForms, control: { type: "radio" } },
    // Use the name that's different from the prop name to hotfix
    // the storybook bug when the prop with a custom type is not updated when
    // the value is set in the URL.
    sVariant: { options: buttonVariants, control: { type: "select" } },
    sSize: { options: buttonSizes, control: { type: "select" } },
    pressed: { control: "boolean" },
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
    return () =>
      h("div", { class: "flex" }, [
        h(
          "div",
          {
            id: "wrapper",
            class: [
              "px-4 h-16 flex items-center justify-center",
              args.sVariant.startsWith("transparent")
                ? "bg-surface"
                : "bg-default",
            ],
          },
          [
            h(
              VButton,
              {
                class: "description-bold",
                href: "/",
                ...args,
                variant: args.sVariant,
                size: args.sSize,
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
          {
            variant: args.sVariant,
            size: args.sSize,
            "has-icon-start": true,
          },
          () => [h(VIcon, { name: "replay" }), "Button"]
        ),
        h(
          VButton,
          {
            variant: args.sVariant,
            size: args.sSize,
            "has-icon-end": true,
          },
          () => ["Button", h(VIcon, { name: "external-link" })]
        ),
        h(
          VButton,
          {
            variant: args.sVariant,
            size: args.sSize,
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
              size: buttonArgs.sSize,
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
    sVariant: "filled-pink-8",
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
    sVariant: "bordered-dark",
  },

  argTypes: {
    pressed: { control: "boolean" },
    sSize: { options: buttonSizes, control: { type: "radio" } },
    sVariant: { options: buttonVariants },
    disabled: { control: "boolean" },
  },
}
