import { h } from "vue"

import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

export default {
  title: "Meta/Focus",
  decorators: [WithScreenshotArea],
}

const GetTemplate = (irrelevantClassNames) => (args) => ({
  setup() {
    return () =>
      h(
        "div",
        {
          class: `h-30 w-30 flex items-center justify-center ${irrelevantClassNames} ${args.classNames.join(" ")}`,
          "data-testid": "focus-target",
          tabindex: "0",
        },
        "Focus on me"
      )
  },
})

export const SlimTransparent = {
  render: GetTemplate("border border-disabled hover:border-hover").bind({}),
  name: "Slim transparent",

  args: {
    classNames: ["focus-slim-tx"],
  },
}

export const SlimFilled = {
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Slim filled",

  args: {
    classNames: ["focus-slim-filled"],
  },
}

export const SlimFilledBorderless = {
  render: GetTemplate("bg-primary text-over-dark").bind({}),
  name: "Slim filled borderless",

  args: {
    classNames: ["focus-slim-borderless-filled"],
  },
}

export const BoldFilled = {
  render: GetTemplate("bg-complementary text-default").bind({}),
  name: "Bold filled",

  args: {
    classNames: ["focus-visible:focus-bold-filled"],
  },
}
