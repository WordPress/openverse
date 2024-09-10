import { h } from "vue"

import VPill from "~/components/VPill.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VPill",
  component: VPill,
  tags: ["autodocs"],
} satisfies Meta<typeof VPill>

export default meta
type Story = StoryObj<typeof meta>

export const VPillStory: Story = {
  render: () => ({
    components: { VPill },
    setup() {
      return () => h(VPill, null, () => "Beta")
    },
  }),
  args: {},
}
