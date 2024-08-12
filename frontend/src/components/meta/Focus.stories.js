import { WithScreenshotArea } from "~~/.storybook/decorators/with-screenshot-area"

const GetTemplate = (irrelevantClassNames) => (args) => ({
  template: `
    <div
      class="h-30 w-30 flex items-center justify-center ${irrelevantClassNames}"
      :class="args.classNames"
      data-testid="focus-target"
      tabindex="0"
    >
      Focus on me
    </div>`,
  setup() {
    return { args }
  },
})

export default {
  title: "Meta/Focus",
  decorators: [WithScreenshotArea],
}

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
  render: GetTemplate("bg-complementary-3 text-default").bind({}),
  name: "Bold filled",

  args: {
    classNames: ["focus-bold-filled"],
  },
}

export const Colored = {
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Colored",

  args: {
    classNames: ["focus-slim-tx-bg-complementary-3"],
  },

  parameters: {
    backgrounds: {
      default: "Dark charcoal",
    },
  },
}
