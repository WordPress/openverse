import { h } from "vue"

import VTag from "~/components/VTag/VTag.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VTag",
  component: VTag,

  argTypes: {
    href: { control: "text" },
  },
  args: {
    href: "#",
  },
} satisfies Meta<typeof VTag>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: (args) => ({
    components: { VTag },
    setup() {
      return () => h(VTag, args, { default: () => "tag" })
    },
  }),
  name: "default",
}
