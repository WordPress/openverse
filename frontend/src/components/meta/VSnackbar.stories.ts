import { h } from "vue"

import VSnackbar from "~/components/VSnackbar.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VSnackbar",
  component: VSnackbar,

  argTypes: {
    size: {
      options: ["large", "small"],
      control: "radio",
    },
    isVisible: {
      control: "boolean",
    },
  },
} satisfies Meta<typeof VSnackbar>

export default meta
type Story = StoryObj<typeof meta>

export const Primary: Story = {
  name: "Primary",
  args: {
    size: "small",
    isVisible: true,
  },
  render: (args) => ({
    components: { VSnackbar },
    setup() {
      return () =>
        h(
          VSnackbar,
          { ...args, style: { display: args.isVisible ? "block" : "none" } },
          { default: () => "Snackbar message" }
        )
    },
  }),
}
