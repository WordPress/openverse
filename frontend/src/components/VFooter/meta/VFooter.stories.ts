import { h } from "vue"

import VFooter from "~/components/VFooter/VFooter.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VFooter",
  component: VFooter,
  parameters: {
    layout: "fullscreen",
    height: "200px",
  },
} satisfies Meta<typeof VFooter>

export default meta
type Story = StoryObj<typeof meta>

const Template: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VFooter },
    setup() {
      return () => h(VFooter, args)
    },
  }),
}

export const Content = {
  ...Template,
  name: "Content",

  args: {
    mode: "content",
  },
}

export const Internal = {
  ...Template,
  name: "Internal",

  args: {
    mode: "internal",
  },
}
