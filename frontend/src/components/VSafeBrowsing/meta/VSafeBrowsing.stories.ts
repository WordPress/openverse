import { h } from "vue"

import VSafeBrowsing from "~/components/VSafeBrowsing/VSafeBrowsing.vue"

import type { StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VSafeBrowsing",
  component: VSafeBrowsing,
  // because it is present in the sidebar
  parameters: {
    viewport: {
      defaultViewport: "xl",
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VSafeBrowsing },
    setup() {
      return () => h(VSafeBrowsing, args)
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",
}
