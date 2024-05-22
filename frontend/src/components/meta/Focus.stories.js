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
  render: GetTemplate(
    "border border-dark-charcoal-40 hover:border-dark-charcoal"
  ).bind({}),
  name: "Slim transparent",

  args: {
    classNames: ["focus-slim-tx"],
  },
}

export const SlimFilled = {
  render: GetTemplate("bg-dark-charcoal text-white border border-tx").bind({}),
  name: "Slim filled",

  args: {
    classNames: ["focus-slim-filled"],
  },
}

export const SlimFilledBorderless = {
  render: GetTemplate("bg-pink text-white").bind({}),
  name: "Slim filled borderless",

  args: {
    classNames: ["focus-slim-borderless-filled"],
  },
}

export const BoldFilled = {
  render: GetTemplate("bg-yellow text-dark-charcoal").bind({}),
  name: "Bold filled",

  args: {
    classNames: ["focus-bold-filled"],
  },
}

export const Colored = {
  render: GetTemplate("bg-dark-charcoal text-white border border-tx").bind({}),
  name: "Colored",

  args: {
    classNames: ["focus-slim-tx-yellow"],
  },

  parameters: {
    backgrounds: {
      default: "Dark charcoal",
    },
  },
}
